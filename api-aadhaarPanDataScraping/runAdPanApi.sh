#!/bin/sh

if [ -f "/home/tssadmin/anaconda3/etc/profile.d/conda.sh" ]; then


    . "/home/tssadmin/anaconda3/etc/profile.d/conda.sh"

    CONDA_CHANGEPS1=false conda activate dt
    echo "Doing Conda activate"
fi

cd /media/tssadmin/e60e6319-b20c-4b74-a6d4-c4f138ac4ebf/api-aadhaarPanDataScraping
uvicorn api_aadhaarPanDetection:app --host 0.0.0.0 --port 8002
