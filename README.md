# 📁 Project File Renamer

A modern web application to organize and rename your project images and annotations with consistent naming patterns.

## ✨ Features

- 🎨 **Beautiful Web UI** - Modern, responsive interface with drag-and-drop support
- 🖼️ **Image Support** - Handle JPG, PNG, GIF, BMP, TIFF, WebP, SVG files
- 📄 **Annotation Support** - Process JSON and TXT annotation files
- 👁️ **Live Preview** - See how files will be renamed before processing
- ⬇️ **Easy Download** - Get organized files in a ZIP archive
- 🐳 **Dockerized** - Run anywhere with Docker

## 📋 Output Format

### Images
Files in `input-images/` → `images/`
- `photo1.jpg` → `{project_name}_image_001.jpg`
- `photo2.png` → `{project_name}_image_002.png`

### Annotations
Files in `output-jsons/` → `annotation/`
- `labels1.txt` → `{project_name}_annotation_001.json`
- `labels2.txt` → `{project_name}_annotation_002.json`

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and run
docker-compose up -d

# Access the app at http://localhost:5173
```

### Option 2: Using Docker

```bash
# Build the image
docker build -t file-renamer .

# Run the container
docker run -p 5173:5173 file-renamer

# Access the app at http://localhost:5173
```

### Option 3: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access the app at http://localhost:5173
```

## 📖 How to Use

1. **Enter Project Name**
   - Type your project name (e.g., "antigravity")
   - This will be used as the prefix for all renamed files

2. **Upload Files**
   - **Images**: Click or drag images to the image upload area
   - **Annotations**: Click or drag JSON/TXT files to the annotation area

3. **Preview Changes** (Optional)
   - Click "👁️ Preview Changes" to see how files will be renamed
   - Review the original → renamed mapping

4. **Download Renamed Files**
   - Click "⬇️ Download Renamed Files"
   - Get a ZIP file with organized structure:
     ```
     project_name/
     ├── images/
     │   ├── project_name_image_001.jpg
     │   └── project_name_image_002.png
     └── annotation/
         ├── project_name_annotation_001.json
         └── project_name_annotation_002.json
     ```

## 🛠️ Technology Stack

- **Backend**: Flask (Python 3.11)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Containerization**: Docker & Docker Compose

## 📁 Project Structure

```
rename-tool/
├── app.py                      # Flask application
├── rename_project_files.py     # Original CLI script
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose configuration
├── .dockerignore              # Docker ignore rules
├── templates/
│   └── index.html             # Main UI template
└── static/
    ├── css/
    │   └── style.css          # Application styles
    └── js/
        └── main.js            # Client-side logic
```

## 🐳 Docker Commands

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Rebuild after changes
docker-compose up -d --build

# Remove containers and volumes
docker-compose down -v
```

## 🔧 Configuration

### Port Configuration
To change the port, edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5173"  # Change 8080 to your desired port
```

### Upload Size Limit
To change the max upload size, edit `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
```

## 🎯 Use Cases

- **Machine Learning Projects**: Organize training datasets with consistent naming
- **Computer Vision**: Prepare image datasets and their annotations
- **Data Labeling**: Standardize labeled data exports
- **Project Organization**: Maintain consistent file naming across projects

## 📝 Original CLI Tool

The original command-line tool is still available:

```bash
python rename_project_files.py /path/to/project_folder
```

This works with folders that have:
- `input-images/` - will be renamed to `images/`
- `output-jsons/` - will be renamed to `annotation/`

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.

## 🎉 Enjoy!

Your files are now organized and ready to use! 🚀
