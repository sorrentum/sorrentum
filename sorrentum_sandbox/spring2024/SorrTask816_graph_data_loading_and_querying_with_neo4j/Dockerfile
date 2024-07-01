# Base Jupyter Notebook Docker Image
FROM jupyter/datascience-notebook

# Disable authentication for JupyterLab
RUN echo "c.NotebookApp.token = ''" >> /home/jovyan/.jupyter/jupyter_notebook_config.py
RUN echo "c.NotebookApp.password = ''" >> /home/jovyan/.jupyter/jupyter_notebook_config.py

COPY requirements.txt ./
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

ENV JUPYTER_ENABLE_LAB=yes

# Copy files into jupyter environment
COPY --chown=${NB_UID}:${NB_GID} ./notebooks /home/jovyan/work/analysis
COPY --chown=${NB_UID}:${NB_GID} ./sh_nw /home/jovyan/work/data

WORKDIR /home/jovyan/work

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--notebook-dir=/home/jovyan/work", "--allow-root"]
