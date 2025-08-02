import os
import pandas as pd
import sympy as sp 
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_FOLDER'] = 'static'

# Ensure upload and static directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATIC_FOLDER'], exist_ok=True)

#function to compute various regression values:
def regression_values(x,y):
    x_bar = x.mean()
    y_bar = y.mean()
    s_xx = ((x-x_bar)**2).sum()
    s_yy = ((y-y_bar)**2).sum()
    s_xy = ((x-x_bar)*(y-y_bar)).sum()
    slope = s_xy/s_xx
    intercept = y_bar - slope*x_bar
    R_squared = s_xy**2/(s_xx*s_yy)
    r = R_squared**0.5
    return round(x_bar, 3), round(y_bar,3), round(s_xx,3), round(s_yy, 3), round(s_xy, 3), round(slope, 3), round(intercept, 3), round(R_squared, 3), round(r, 3)



#function to display regression line equation
def display_regression_equation(slope, intercept):
    x, y = sp.symbols('x y')
    
    # Create the equation: y = slope * x + intercept
    eqn = sp.Eq(y, slope * x + intercept)
    
    # Display the equation in LaTeX using Streamlit
    return sp.latex(eqn)


#plot scatter plot and regression line
def plot_line(x, y, y_pred, filename='line_plot.png'):
    plt.figure(figsize=(6, 4))
    plt.plot(x, y_pred, color='green', label=' Regression Line')
    plt.scatter(x, y, color='blue', label='Data Points')
    plt.scatter(x,y_pred, color = 'red', label = 'Predicted Points')
    plt.title('Scatter Plot and Regression Line')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid()
    plt.legend()
    
    # Save the plot to the static folder
    plot_path = os.path.join('static', filename)
    plt.savefig(plot_path)
    plt.close()
    return filename




@app.route('/', methods=['GET', 'POST'])
def index():
    plot_url = None
    plot_url1 = None
    error = None
    reg_values = None
    reg_eqn = None

    if request.method == 'POST':
        file = request.files.get('file')

        if not file:
            error = "No file uploaded."
        elif not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            error = "Please upload a CSV or XLSX file."
        else:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            try:
                # Read the file
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_excel(filepath)

                # Check for at least 2 columns
                if df.shape[1] < 2:
                    error = "File must contain at least two columns."
                else:
                    x = df.iloc[:, 0]
                    y = df.iloc[:, 1]

                    # Plot
                    
                    reg_values = regression_values(x,y)
                    a,b,c,d,e,f,g,h,i = regression_values(x,y)
                    y_pred = f*x + g
                    reg_eqn = display_regression_equation(f, g)
                    filename = plot_line(x,y,y_pred)
                    plot_url1 = url_for('static', filename = filename)
                    



            except Exception as e:
                error = f"Error processing file: {e}"

    return render_template('index.html', plot_url=plot_url, plot_url1 = plot_url1, reg_values = reg_values, reg_eqn = reg_eqn,  error=error)

if __name__ == '__main__':
    app.run(debug=True)
