FROM continuumio/miniconda3:latest AS miniconda

# Add conda to the path
RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc

# Switch over the shell version
SHELL ["/bin/bash", "-c"]

# Install dependencies
RUN apt-get update --fix-missing -y \
    && apt-get install -y \
        build-essential \
        libxrender-dev \
        libsm6 \
        libglib2.0-0 \
        vim-gtk3 \
        libgl1-mesa-dev

# Arguments for cloning down the repos and installing them to the conda environment
ARG GIT_NAME
ARG SERVICE_TOKEN

# Create and install all moseq2 packages to the environment
RUN source ~/.bashrc \
    && conda update -n base -c defaults conda \
    && conda create -n moseq2 python=3.6 -y \
    && conda activate moseq2 \
    && conda install -c conda-forge ffmpeg \
    && conda install --yes -c conda-forge scikit-image \
    # NOTE: THIS IS A HACK!!! LATEST VERSION OF SCIKIT DOES NOT WORK
    && pip install requests future cython "pytest>=3.6" pytest-cov codecov \
    && pip install git+https://github.com/tischfieldlab/pyhsmm.git \
    && pip install git+https://github.com/tischfieldlab/pyhsmm-autoregressive.git \
    && pip install git+https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-extract.git \
    && pip install git+https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-pca.git \
    # NOTE: Forward install all the pre-reqs for moseq2-model so that we don't rely on broken URL paths in the setup.py file
    && pip install future h5py click numpy "joblib==0.13.1" hdf5storage "ruamel.yaml>=0.15.0" tqdm \
    && pip install git+https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-model.git --no-deps \
    && pip install git+https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-batch.git \
    && pip install git+https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-viz.git \
    && pip install git+https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-extras.git

# Run tests to make sure all repos work
RUN source activate moseq2 \
    && git clone https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-extras.git \
    && pytest moseq2-extras/tests/test_entry_points.py \
    && mkdir /moseq2_data \
    && mkdir /moseq2_data/flip_files \
    && rm -rf moseq2-extras

# Copy the classifiers
COPY flip_files/*.pkl /moseq2_data/flip_files/

# Copy the argtable.py file in the image to run
COPY argtable.py /tmp/

# Run the script to generate the argtables
RUN source activate moseq2 \
    && apt install python-skimage \
    && conda install -c conda-forge tifffile \
    && python /tmp/argtable.py --output-file /moseq2_data/argtable.yaml \
    && cat /moseq2_data/argtable.yaml \
    && rm /tmp/argtable.py

# Create the requirements.txt file
RUN source activate moseq2 \
    && pip freeze > /tmp/pipfreeze.txt  \
    && conda list > /tmp/condalist.txt \
    && apt list --installed > /tmp/aptpackages.txt \
    && cat /etc/os-release > /tmp/containerinfo.txt \
    && docker -v > /tmp/dockerversion.txt \
    && singularity version > /tmp/singularityversion.txt \
    && pwd && ls

# Add env activation in bashrc file
RUN echo 'source activate moseq2' >> ~/.bashrc

# Initialize the shell for conda and activate moseq2 on startupa
SHELL ["conda", "run", "-n", "moseq2", "/bin/bash", "-c"]