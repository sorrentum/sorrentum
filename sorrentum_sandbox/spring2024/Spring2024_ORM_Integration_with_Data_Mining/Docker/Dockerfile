FROM python:latest

# Install Jupyter Notebook
RUN pip install jupyter -U && pip install jupyterlab

# Install required Python libraries
RUN pip install numpy pandas matplotlib seaborn wordcloud plotly scikit-learn lightgbm sqlalchemy

# Set working directory
WORKDIR /app	

# Set port
EXPOSE 8888

# Install IPython kernel for Python
RUN python -m ipykernel install --user --name=myenv

# Default command to run when the container starts
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root"]
