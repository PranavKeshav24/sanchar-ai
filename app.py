from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json
import random
from datetime import datetime
from data_loader import load_vehicle_data, get_random_vehicles
from simulation import SimulationEngine, TrafficPredictor
import threading
import time
import numpy as np
import os
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for, flash
import cv2
import torch
import numpy as np
import sqlite3
import os
from datetime import datetime
import threading
from werkzeug.utils import secure_filename
import json
import time

app = Flask(__name__)
app.config.from_object('config.Config')
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Initialize simulation engine and traffic predictor
simulation_engine = SimulationEngine()
traffic_predictor = TrafficPredictor()

# Allowed video extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'mkv', 'flv'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize models
MODELS = {
    'accident': 'models/ACCIDENT.pt',
    'pothole': 'models/pathole_hump.pt'
}

# Global variables for processing
processing_videos = {}
live_camera = None
live_detection_active = False
current_live_detection_type = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS complaints
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  detection_type TEXT,
                  confidence REAL,
                  timestamp TEXT,
                  location TEXT,
                  description TEXT,
                  image_path TEXT)''')
    conn.commit()
    conn.close()

init_db()

def get_model(detection_type):
    """Load and return the appropriate model"""
    model_path = MODELS.get(detection_type)
    if model_path and os.path.exists(model_path):
        try:
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=False)
            model.conf = 0.25
            return model
        except Exception as e:
            print(f"Error loading model {detection_type}: {e}")
            return None
    else:
        print(f"Model path not found: {model_path}")
        return None

def save_complaint(detection_type, confidence, image_path=None, description=""):
    """Save detection as a complaint in database"""
    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    c.execute('''INSERT INTO complaints 
                 (detection_type, confidence, timestamp, location, description, image_path) 
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (detection_type, confidence, timestamp, "Live Detection", description, image_path))
    conn.commit()
    conn.close()

def generate_live_frames(detection_type):
    """Generate live camera frames with object detection"""
    global live_camera, live_detection_active
    
    model = get_model(detection_type)
    if not model:
        # Return a black frame if model fails to load
        black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(black_frame, "Model not available", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        ret, buffer = cv2.imencode('.jpg', black_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        return
    
    live_camera = cv2.VideoCapture(0)
    live_detection_active = True
    
    while live_detection_active:
        success, frame = live_camera.read()
        if not success:
            break
        
        try:
            # Perform detection
            results = model(frame)
            predictions = results.pandas().xyxy[0]
            
            # Draw bounding boxes and labels
            for _, row in predictions.iterrows():
                if row['confidence'] > 0.25:  # Confidence threshold
                    x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
                    label = f"{row['name']} {row['confidence']:.2f}"
                    color = (0, 255, 0) if detection_type == 'pothole' else (0, 0, 255)
                    
                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw label background
                    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                    cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), (x1 + label_size[0], y1), color, -1)
                    
                    # Draw label text
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Save high confidence detections
                    if row['confidence'] > 0.7:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        image_path = f"static/uploads/live_detection_{timestamp}.jpg"
                        cv2.imwrite(image_path, frame)
                        save_complaint(detection_type, float(row['confidence']), image_path,
                                     "Detected in live camera feed")
            
            # Add status overlay
            cv2.putText(frame, f"Live {detection_type.title()} Detection", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "Press 'q' to quit", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                       
        except Exception as e:
            print(f"Live detection error: {e}")
            cv2.putText(frame, f"Error: {str(e)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    if live_camera:
        live_camera.release()

def generate_processed_frames(video_path, detection_type, session_id):
    """Generate processed video frames with bounding boxes"""
    model = get_model(detection_type)
    if not model:
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + 
               cv2.imencode('.jpg', np.zeros((480, 640, 3), dtype=np.uint8))[1].tobytes() + 
               b'\r\n')
        return
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    processing_videos[session_id] = {
        'status': 'processing',
        'current_frame': 0,
        'total_frames': total_frames,
        'detections': []
    }
    
    frame_count = 0
    detections_found = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        processing_videos[session_id]['current_frame'] = frame_count
        
        # Perform detection on every frame for real-time streaming
        try:
            results = model(frame)
            predictions = results.pandas().xyxy[0]
            
            frame_detections = []
            
            # Draw bounding boxes and labels
            for _, row in predictions.iterrows():
                if row['confidence'] > 0.25:  # Confidence threshold
                    x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
                    label = f"{row['name']} {row['confidence']:.2f}"
                    color = (0, 255, 0) if detection_type == 'pothole' else (0, 0, 255)
                    
                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw label background
                    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                    cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), (x1 + label_size[0], y1), color, -1)
                    
                    # Draw label text
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    detection_info = {
                        'frame': frame_count,
                        'type': row['name'],
                        'confidence': float(row['confidence']),
                        'bbox': [x1, y1, x2, y2]
                    }
                    frame_detections.append(detection_info)
                    
                    # Save high confidence detections
                    if row['confidence'] > 0.7:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        image_path = f"static/uploads/detection_{timestamp}_{frame_count}.jpg"
                        cv2.imwrite(image_path, frame)
                        save_complaint(detection_type, float(row['confidence']), image_path,
                                     f"Detected in uploaded video at frame {frame_count}")
                        detections_found += 1
            
            if frame_detections:
                processing_videos[session_id]['detections'].extend(frame_detections)
                
        except Exception as e:
            print(f"Error processing frame {frame_count}: {e}")
        
        # Add processing info overlay
        progress = (frame_count / total_frames) * 100
        info_text = f"Frame: {frame_count}/{total_frames} | Detections: {detections_found} | Progress: {progress:.1f}%"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Detection: {detection_type}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Resize frame for faster streaming if needed
        frame = resize_frame(frame, max_width=800)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Small delay to simulate real-time processing (adjust as needed)
        time.sleep(0.03)  # ~30 FPS
    
    cap.release()
    processing_videos[session_id]['status'] = 'completed'
    processing_videos[session_id]['total_detections'] = detections_found
    
    print(f"Video processing completed. Total detections: {detections_found}")

def resize_frame(frame, max_width=800):
    """Resize frame while maintaining aspect ratio"""
    height, width = frame.shape[:2]
    if width > max_width:
        ratio = max_width / width
        new_width = max_width
        new_height = int(height * ratio)
        frame = cv2.resize(frame, (new_width, new_height))
    return frame
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('index1.html')

@app.route('/live_detection')
def live_detection():
    return render_template('live_detection.html')

@app.route('/video_feed/<detection_type>')
def video_feed(detection_type):
    """Live camera feed with detection"""
    return Response(generate_live_frames(detection_type),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_live_detection/<detection_type>')
def start_live_detection(detection_type):
    """Start live detection"""
    global current_live_detection_type
    current_live_detection_type = detection_type
    return jsonify({'status': 'started', 'type': detection_type})

@app.route('/stop_live_detection')
def stop_live_detection():
    """Stop live detection"""
    global live_detection_active, live_camera
    live_detection_active = False
    if live_camera:
        live_camera.release()
        live_camera = None
    return jsonify({'status': 'stopped'})

@app.route('/video_upload')
def video_upload():
    return render_template('video_upload.html')

@app.route('/video_stream/<session_id>')
def video_stream(session_id):
    """Stream processed video with detections"""
    video_info = processing_videos.get(session_id)
    if not video_info:
        return "Video not found", 404
    
    video_path = video_info['video_path']
    detection_type = video_info['detection_type']
    
    return Response(generate_processed_frames(video_path, detection_type, session_id),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload_video', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file uploaded'}), 400
        
        file = request.files['video']
        detection_type = request.form.get('detection_type', 'pothole')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Create unique session ID for this processing job
            session_id = f"{int(time.time())}_{filename}"
            
            # Store video info
            processing_videos[session_id] = {
                'filename': filename,
                'video_path': filepath,
                'detection_type': detection_type,
                'status': 'uploaded',
                'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return jsonify({
                'status': 'success',
                'message': 'Video uploaded successfully',
                'session_id': session_id,
                'filename': filename
            })
        else:
            return jsonify({'error': 'Invalid file type. Allowed types: mp4, avi, mov, wmv, mkv, flv'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/get_processing_status/<session_id>')
def get_processing_status(session_id):
    """Get current processing status"""
    video_info = processing_videos.get(session_id)
    if not video_info:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'status': video_info.get('status', 'unknown'),
        'current_frame': video_info.get('current_frame', 0),
        'total_frames': video_info.get('total_frames', 0),
        'detections': video_info.get('detections', []),
        'total_detections': video_info.get('total_detections', 0)
    })

@app.route('/get_detection_results/<session_id>')
def get_detection_results(session_id):
    """Get final detection results"""
    video_info = processing_videos.get(session_id)
    if not video_info:
        return jsonify({'error': 'Session not found'}), 404
    
    if video_info.get('status') != 'completed':
        return jsonify({'error': 'Processing not completed'}), 400
    
    return jsonify({
        'status': 'completed',
        'total_detections': video_info.get('total_detections', 0),
        'detections': video_info.get('detections', []),
        'filename': video_info.get('filename', ''),
        'detection_type': video_info.get('detection_type', '')
    })

@app.route('/complaints')
def complaints():
    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    c.execute('SELECT * FROM complaints ORDER BY timestamp DESC')
    complaints_data = c.fetchall()
    conn.close()
    
    return render_template('complaints.html', complaints=complaints_data)

@app.route('/add_complaint', methods=['POST'])
def add_complaint():
    detection_type = request.form.get('detection_type')
    description = request.form.get('description')
    
    if not detection_type or not description:
        flash('Please fill in all fields', 'error')
        return redirect(url_for('complaints'))
    
    save_complaint(detection_type, 1.0, None, description)
    flash('Complaint added successfully!', 'success')
    
    return redirect(url_for('complaints'))

@app.route('/delete_complaint/<int:complaint_id>')
def delete_complaint(complaint_id):
    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    
    # Get image path before deletion
    c.execute('SELECT image_path FROM complaints WHERE id = ?', (complaint_id,))
    result = c.fetchone()
    
    # Delete the complaint
    c.execute('DELETE FROM complaints WHERE id = ?', (complaint_id,))
    conn.commit()
    conn.close()
    
    # Delete associated image file if it exists
    if result and result[0] and os.path.exists(result[0]):
        try:
            os.remove(result[0])
        except Exception as e:
            print(f"Error deleting image file: {e}")
    
    flash('Complaint deleted successfully!', 'success')
    return redirect(url_for('complaints'))
# @app.route('/Pathole_Detect')
# def Pathole_Detect():
#     os.system('python pathole_hump.py')
#     flash('Pathhole Detected at complaint raised', 'danger')
#     return render_template('dashboard.html')

# @app.route('/Accident_Detect')
# def Accident_Detect():
#     os.system('python accident_detection.py')
#     return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if not username or not email or not password:
            flash('Please fill all fields', 'error')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration', 'error')
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', username=session['username'])

@app.route('/simulation')
def simulation():
    if 'user_id' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))
    
    return render_template('simulation.html')

@app.route('/get_vehicle_data')
def get_vehicle_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401
        
    vehicle_count = session.get('vehicle_count', 5) * 4  # 4 roads
    vehicles = get_random_vehicles(vehicle_count)
    
    # Update simulation engine configuration
    simulation_engine.update_config(
        session.get('vehicle_count', 5),
        session.get('ai_prediction', True),
        session.get('emergency_priority', True)
    )
    
    simulation_engine.set_vehicles(vehicles)
    return jsonify(vehicles)

@app.route('/start_simulation')
def start_simulation():
    simulation_engine.start()
    return jsonify({'status': 'started'})

@app.route('/stop_simulation')
def stop_simulation():
    simulation_engine.stop()
    return jsonify({'status': 'stopped'})

@app.route('/get_simulation_state')
def get_simulation_state():
    try:
        return jsonify(simulation_engine.get_state())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_simulation_stats')
def get_simulation_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401
        
    # Calculate statistics from simulation
    vehicles = simulation_engine.vehicles
    if vehicles:
        avg_speed = sum(v['speed'] for v in vehicles) / len(vehicles)
        avg_latency = sum(v.get('latency', 0) for v in vehicles) / len(vehicles)
        avg_signal = sum(v.get('signal_strength', 0) for v in vehicles) / len(vehicles)
    else:
        avg_speed, avg_latency, avg_signal = 0, 0, 0
        
    return jsonify({
        'active_vehicles': len(vehicles),
        'avg_speed': round(avg_speed, 1),
        'avg_latency': round(avg_latency, 1),
        'avg_signal': round(avg_signal, 1)
    })

@app.route('/update_config', methods=['POST'])
def update_config():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401
        
    data = request.get_json()
    session['vehicle_count'] = int(data.get('vehicle_count', 5))
    session['ai_prediction'] = bool(data.get('ai_prediction', True))
    session['emergency_priority'] = bool(data.get('emergency_priority', True))
    
    return jsonify({'status': 'success'})

# Add vehicles to specific roads
@app.route('/add_vehicles_north')
def add_vehicles_north():
    simulation_engine.add_vehicles_to_road('north', 3)
    return jsonify({'status': 'vehicles added to north'})

@app.route('/add_vehicles_south')
def add_vehicles_south():
    simulation_engine.add_vehicles_to_road('south', 3)
    return jsonify({'status': 'vehicles added to south'})

@app.route('/add_vehicles_east')
def add_vehicles_east():
    simulation_engine.add_vehicles_to_road('east', 3)
    return jsonify({'status': 'vehicles added to east'})

@app.route('/add_vehicles_west')
def add_vehicles_west():
    simulation_engine.add_vehicles_to_road('west', 3)
    return jsonify({'status': 'vehicles added to west'})

# Add ambulance to specific roads with priority
@app.route('/add_ambulance_north')
def add_ambulance_north():
    simulation_engine.add_ambulance_with_priority('north')
    return jsonify({'status': 'ambulance added to north with priority'})

@app.route('/add_ambulance_south')
def add_ambulance_south():
    simulation_engine.add_ambulance_with_priority('south')
    return jsonify({'status': 'ambulance added to south with priority'})

@app.route('/add_ambulance_east')
def add_ambulance_east():
    simulation_engine.add_ambulance_with_priority('east')
    return jsonify({'status': 'ambulance added to east with priority'})

@app.route('/add_ambulance_west')
def add_ambulance_west():
    simulation_engine.add_ambulance_with_priority('west')
    return jsonify({'status': 'ambulance added to west with priority'})

@app.route('/clear_all_vehicles')
def clear_all_vehicles():
    simulation_engine.clear_all_vehicles()
    return jsonify({'status': 'all vehicles cleared'})

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)