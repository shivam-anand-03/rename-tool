#!/usr/bin/env python3
"""Flask web application for renaming project files with a UI."""

import os
import shutil
import zipfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'svg'}
ALLOWED_JSON_EXTENSIONS = {'json', 'txt'}


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def rename_files_in_memory(images, jsons, project_name):
    """Rename files according to the pattern and return renamed file info."""
    renamed_images = []
    renamed_jsons = []
    
    # Sort images by original filename
    sorted_images = sorted(images, key=lambda x: x.filename)
    
    # Rename images
    for idx, image in enumerate(sorted_images, start=1):
        original_name = image.filename
        _, ext = os.path.splitext(original_name)
        new_name = f"{project_name}_image_{idx:03d}{ext}"
        renamed_images.append({
            'original': original_name,
            'renamed': new_name,
            'file': image
        })
    
    # Sort JSONs by original filename
    sorted_jsons = sorted(jsons, key=lambda x: x.filename)
    
    # Rename JSONs (force .json extension)
    for idx, json_file in enumerate(sorted_jsons, start=1):
        original_name = json_file.filename
        new_name = f"{project_name}_annotation_{idx:03d}.json"
        renamed_jsons.append({
            'original': original_name,
            'renamed': new_name,
            'file': json_file
        })
    
    return renamed_images, renamed_jsons


def create_project_structure(project_name, renamed_images, renamed_jsons):
    """Create the project folder structure and save files."""
    # Create temporary directory for the project
    temp_dir = tempfile.mkdtemp()
    project_dir = os.path.join(temp_dir, project_name)
    os.makedirs(project_dir)
    
    # Create images folder
    if renamed_images:
        images_dir = os.path.join(project_dir, 'images')
        os.makedirs(images_dir)
        for item in renamed_images:
            file_path = os.path.join(images_dir, item['renamed'])
            item['file'].save(file_path)
    
    # Create annotation folder
    if renamed_jsons:
        annotation_dir = os.path.join(project_dir, 'annotation')
        os.makedirs(annotation_dir)
        for item in renamed_jsons:
            file_path = os.path.join(annotation_dir, item['renamed'])
            item['file'].save(file_path)
    
    # Create a zip file
    zip_path = os.path.join(temp_dir, f"{project_name}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    return zip_path, project_dir


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/preview', methods=['POST'])
def preview():
    """Preview the renamed files without actually saving them."""
    try:
        project_name = request.form.get('project_name', '').strip()
        if not project_name:
            return jsonify({'error': 'Project name is required'}), 400
        
        # Get uploaded files
        images = request.files.getlist('images')
        jsons = request.files.getlist('jsons')
        
        if not images and not jsons:
            return jsonify({'error': 'Please upload at least one file'}), 400
        
        # Validate files
        for img in images:
            if img.filename and not allowed_file(img.filename, ALLOWED_IMAGE_EXTENSIONS):
                return jsonify({'error': f'Invalid image file: {img.filename}'}), 400
        
        for json_file in jsons:
            if json_file.filename and not allowed_file(json_file.filename, ALLOWED_JSON_EXTENSIONS):
                return jsonify({'error': f'Invalid annotation file: {json_file.filename}'}), 400
        
        # Filter out empty files
        images = [img for img in images if img.filename]
        jsons = [j for j in jsons if j.filename]
        
        # Get renamed file info
        renamed_images, renamed_jsons = rename_files_in_memory(images, jsons, project_name)
        
        # Prepare response
        response = {
            'project_name': project_name,
            'images': [{'original': img['original'], 'renamed': img['renamed']} for img in renamed_images],
            'jsons': [{'original': j['original'], 'renamed': j['renamed']} for j in renamed_jsons]
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/process', methods=['POST'])
def process():
    """Process and download the renamed files."""
    try:
        project_name = request.form.get('project_name', '').strip()
        if not project_name:
            return jsonify({'error': 'Project name is required'}), 400
        
        # Get uploaded files
        images = request.files.getlist('images')
        jsons = request.files.getlist('jsons')
        
        if not images and not jsons:
            return jsonify({'error': 'Please upload at least one file'}), 400
        
        # Validate files
        for img in images:
            if img.filename and not allowed_file(img.filename, ALLOWED_IMAGE_EXTENSIONS):
                return jsonify({'error': f'Invalid image file: {img.filename}'}), 400
        
        for json_file in jsons:
            if json_file.filename and not allowed_file(json_file.filename, ALLOWED_JSON_EXTENSIONS):
                return jsonify({'error': f'Invalid annotation file: {json_file.filename}'}), 400
        
        # Filter out empty files
        images = [img for img in images if img.filename]
        jsons = [j for j in jsons if j.filename]
        
        # Get renamed file info
        renamed_images, renamed_jsons = rename_files_in_memory(images, jsons, project_name)
        
        # Create project structure and zip
        zip_path, project_dir = create_project_structure(project_name, renamed_images, renamed_jsons)
        
        # Send the zip file
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"{project_name}.zip",
            mimetype='application/zip'
        )
    
    except Exception as e:
        app.logger.error(f"Error processing files: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5173, debug=True)
