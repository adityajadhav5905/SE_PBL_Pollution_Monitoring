from flask import Flask, request, jsonify, send_file, render_template
import pandas as pd
import folium
from folium.plugins import HeatMap
import os
import glob
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sklearn.preprocessing import MinMaxScaler

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# Configuration
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'csv'}

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_heatmap(df, value_column, output_html, output_png):
    """Generate heatmap for a specific value column, zoomed to data points"""
    try:
        app.logger.debug(f"Creating heatmap for column: {value_column}")
        
        # Validate data types
        if not all(df['Latitude'].apply(lambda x: isinstance(x, (int, float)))):
            app.logger.error(f"Invalid Latitude data for {value_column}")
            return None, "Latitude contains non-numeric values"
        if not all(df['Longitude'].apply(lambda x: isinstance(x, (int, float)))):
            app.logger.error(f"Invalid Longitude data for {value_column}")
            return None, "Longitude contains non-numeric values"
        if not all(df[value_column].apply(lambda x: isinstance(x, (int, float)))):
            app.logger.error(f"Invalid data in column {value_column}: non-numeric values")
            return None, f"{value_column} contains non-numeric values"

        # Normalize the value column
        try:
            scaler = MinMaxScaler()
            df[f'{value_column}_normalized'] = scaler.fit_transform(df[[value_column]])
        except Exception as e:
            app.logger.error(f"Normalization failed for {value_column}: {str(e)}")
            return None, f"Normalization failed for {value_column}: {str(e)}"

        # Extract coordinates
        lat = df['Latitude']
        lon = df['Longitude']
        
        # Calculate bounds
        try:
            min_lat, max_lat = lat.min(), lat.max()
            min_lon, max_lon = lon.min(), lon.max()
            lat_center = lat.mean()
            lon_center = lon.mean()
        except Exception as e:
            app.logger.error(f"Bounds calculation failed for {value_column}: {str(e)}")
            return None, f"Bounds calculation failed: {str(e)}"

        # Validate bounds
        if min_lat == max_lat or min_lon == max_lon:
            app.logger.error(f"Invalid bounds for {value_column}: identical coordinates")
            return None, "All points have identical coordinates"

        # Create base map
        heatmap = folium.Map(
            location=[lat_center, lon_center],
            tiles='CartoDB positron',
            zoom_start=5,  # Fallback, overridden by fit_bounds
            control_scale=False,
            zoom_control=False,
            scrollWheelZoom=False
        )
        
        # Set map bounds to fit all data points
        try:
            heatmap.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]], padding=(50, 50))
        except Exception as e:
            app.logger.error(f"Fit bounds failed for {value_column}: {str(e)}")
            return None, f"Fit bounds failed: {str(e)}"
        
        # Prepare heatmap data
        heat_data = [[row['Latitude'], row['Longitude'], row[f'{value_column}_normalized']] 
                     for _, row in df.iterrows()]
        
        # Define gradient
        gradient = {
            0.0: '#00e400',  # Green
            0.2: '#ffff00',  # Yellow
            0.4: '#ff7e00',  # Orange
            0.6: '#ff0000',  # Red
            0.8: '#8f3f97',  # Purple
            1.0: '#7e0023',  # Maroon
        }

        # Add heatmap layer
        try:
            HeatMap(
                heat_data,
                radius=36,
                blur=55,
                min_opacity=0.01,
                max_opacity=0.05,
                gradient=gradient
            ).add_to(heatmap)
        except Exception as e:
            app.logger.error(f"Heatmap creation failed for {value_column}: {str(e)}")
            return None, f"Heatmap creation failed for {value_column}: {str(e)}"
        
        # Save heatmap as HTML
        try:
            heatmap.save(output_html)
            app.logger.debug(f"Saved HTML: {output_html}")
        except Exception as e:
            app.logger.error(f"Failed to save HTML for {value_column}: {str(e)}")
            return None, f"Failed to save HTML: {str(e)}"
        
        # Generate PNG
        success, error = save_map_as_png(output_html, output_png)
        if not success:
            app.logger.error(f"PNG generation failed for {value_column}: {error}")
            return None, f"PNG generation failed for {value_column}: {error}"
        
        # Verify PNG exists
        for _ in range(10):
            if os.path.exists(output_png):
                app.logger.debug(f"Confirmed PNG exists: {output_png}")
                break
            time.sleep(0.5)
        else:
            app.logger.error(f"PNG file not found after creation: {output_png}")
            return None, f"PNG file {output_png} was not created"
        
        return heatmap, None
    except Exception as e:
        app.logger.error(f"Unexpected error in heatmap creation for {value_column}: {str(e)}")
        return None, f"Unexpected error in heatmap creation for {value_column}: {str(e)}"

def save_map_as_png(html_path, png_path):
    """Convert Folium map HTML to PNG using Selenium"""
    try:
        # Configure headless Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1280,720")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Load the HTML file
        driver.get(f"file://{os.path.abspath(html_path)}")
        
        # Wait for map to render
        time.sleep(3)
        
        # Save screenshot
        driver.save_screenshot(png_path)
        
        driver.quit()
        app.logger.debug(f"Saved PNG: {png_path}")
        return True, None
    except Exception as e:
        app.logger.error(f"Error generating PNG: {str(e)}")
        return False, f"Error generating PNG: {str(e)}"

@app.route('/')
def home():
    """Render the main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and generate heatmaps for all pollutant columns"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        # Validate file
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a CSV file'}), 400
        
        # Read CSV file
        try:
            df = pd.read_csv(file)
            app.logger.debug(f"CSV columns: {df.columns.tolist()}")
        except Exception as e:
            app.logger.error(f"Error reading CSV file: {str(e)}")
            return jsonify({'error': f'Error reading CSV file: {str(e)}'}), 400
        
        # Validate required columns (at least Latitude, Longitude)
        required_columns = ['Latitude', 'Longitude']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            app.logger.error(f"Missing columns: {missing_columns}")
            return jsonify({'error': f'Missing required columns: {", ".join(missing_columns)}'}), 400
        
        # Drop rows with missing GPS data
        df = df.dropna(subset=required_columns)
        if df.empty:
            app.logger.error("No valid data after removing missing GPS values")
            return jsonify({'error': 'No valid data after removing missing GPS values'}), 400

        # Identify pollutant columns (third column onward)
        pollutant_columns = df.columns[2:].tolist()
        if not pollutant_columns:
            app.logger.error("No pollutant columns found")
            return jsonify({'error': 'No pollutant data columns found (third column onward)'}), 400
        app.logger.debug(f"Pollutant columns: {pollutant_columns}")

        # Generate heatmaps for each pollutant
        results = []
        for col in pollutant_columns:
            app.logger.debug(f"Processing column: {col}")
            # Skip if column has no valid data
            if df[col].dropna().empty:
                app.logger.warning(f"No valid data for {col}")
                results.append({'column': col, 'error': f'No valid data for {col}'})
                continue
            
            # Create heatmap
            html_path = os.path.join(UPLOAD_FOLDER, f'heatmap_{col.replace(" ", "_")}.html')
            png_path = os.path.join(UPLOAD_FOLDER, f'heatmap_{col.replace(" ", "_")}.png')
            heatmap, error = create_heatmap(df, col, html_path, png_path)
            if heatmap is None:
                app.logger.error(f"Failed to create heatmap for {col}: {error}")
                results.append({'column': col, 'error': error})
            else:
                results.append({'column': col, 'map_path': f'/{png_path}'})

        # Check if any heatmaps were successful
        successful = [r for r in results if 'map_path' in r]
        if not successful:
            app.logger.error("No heatmaps created successfully")
            return jsonify({'error': 'Failed to create any heatmaps', 'details': results}), 500

        app.logger.info(f"Heatmaps generated: {[r.get('map_path') for r in successful]}")
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        app.logger.error(f"Unexpected error in upload: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    """Serve a specific heatmap file"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        app.logger.debug(f"Attempting to download: {file_path}")
        if not os.path.exists(file_path):
            app.logger.error(f"File not found: {file_path}")
            return jsonify({'error': f'File {filename} not found'}), 404
        app.logger.info(f"Serving file: {file_path}")
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        app.logger.error(f"Download error for {filename}: {str(e)}")
        return jsonify({'error': f'Error serving file: {str(e)}'}), 500

@app.route('/clear', methods=['POST'])
def clear_files():
    """Delete all temporary PNG and HTML files in the static folder"""
    try:
        # Define patterns for files to delete
        patterns = [
            os.path.join(UPLOAD_FOLDER, 'heatmap_*.png'),
            os.path.join(UPLOAD_FOLDER, 'heatmap_*.html')
        ]
        
        deleted_files = []
        for pattern in patterns:
            for file_path in glob.glob(pattern):
                try:
                    os.remove(file_path)
                    deleted_files.append(file_path)
                except Exception as e:
                    app.logger.warning(f"Failed to delete {file_path}: {str(e)}")
                    continue
        
        app.logger.info(f"Cleared files: {deleted_files}")
        return jsonify({'success': True, 'deleted': deleted_files})
    except Exception as e:
        app.logger.error(f"Clear files error: {str(e)}")
        return jsonify({'error': f'Failed to clear files: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)