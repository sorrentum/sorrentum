FROM jupyter/datascience-notebook

COPY requirements.txt ./
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /home/jovyan/work

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--notebook-dir=/home/jovyan/work", "--allow-root", "--NotebookApp.token=''"]