FROM continuumio/miniconda3:latest AS miniconda

# Add conda to the path
RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc

# Switch over the shell version
SHELL ["/bin/bash", "-c"]

# Install dependencies
RUN apt-get update --fix-missing -y \
    && apt-get install build-essential \
    libxrender-dev libsm6 libglib2.0-0 vim-gtk3 -y

# Arguments for cloning down the repos and installing them to the conda environment
ARG GIT_NAME
ARG SERVICE_TOKEN

# Create and install all moseq2 packages to the environment
RUN source ~/.bashrc \
    && conda update -n base -c defaults conda \
    && conda create -n moseq2 python=3.6 -y \
    && conda install -c conda-forge ffmpeg \
    && conda activate moseq2 \
    && pip install requests future cython \
    && pip install git+https://github.com/tischfieldlab/pyhsmm.git \
    && pip install git+https://github.com/tischfieldlab/pyhsmm-autoregressive.git \
    && pip install git+https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-extract.git \
    && pip install git+https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-pca.git \
    && pip install git+https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-model.git \
    && pip install git+https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-batch.git \
    && pip install git+https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-viz.git \
    && pip install git+https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-extras.git

# Run tests to make sure all repos work
RUN source activate moseq2 \
    && git clone https://${GIT_NAME}:${SERVICE_TOKEN}@github.com/tischfieldlab/moseq2-extras.git \
    && pip install "pytest>=3.6" pytest-cov codecov \
    # NOTE: THIS IS A HACK!!! LATEST VERSION OF SCIKIT DOES NOT WORK
    && pip install scikit-image==0.16.2 \ 
    && pytest moseq2-extras/tests/test_entry_points.py \
    && rm -rf moseq2-extras \
    && mkdir /moseq2_data \
    && mkdir /moseq2_data/flip_files \
    # Download the flip classifier to a known directory
    && moseq2-extract download-flip-file --output-dir /moseq2_data/flip_files <<< "0" \
    && moseq2-extract download-flip-file --output-dir /moseq2_data/flip_files <<< "1" \
    && moseq2-extract download-flip-file --output-dir /moseq2_data/flip_files <<< "2"

# Add env activation in bashrc file
RUN echo 'source actiavte moseq2' >> ~/.bashrc

# Initialize the shell for conda and activate moseq2 on startup
SHELL ["conda", "run", "-n", "moseq2", "/bin/bash", "-c"]

# Setup entry point for bash
ENTRYPOINT ["/bin/bash"]
