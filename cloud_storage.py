import boto3
from pathlib import Path
import os
from botocore.config import Config
import streamlit as st

class CloudStorage:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=os.getenv('R2_ENDPOINT'),
            aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        self.bucket = os.getenv('R2_BUCKET_NAME', 'drivesense-telemetry')
        self.local_cache = Path('/tmp/processed_data')
    
    def ensure_data_downloaded(self):
        if self.local_cache.exists():
            return True
        
        self.local_cache.mkdir(parents=True, exist_ok=True)
        
        try:
            paginator = self.s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket, Prefix='processed_data/')
            
            files_to_download = []
            for page in pages:
                if 'Contents' in page:
                    files_to_download.extend([obj['Key'] for obj in page['Contents']])
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, key in enumerate(files_to_download):
                local_path = Path('/tmp') / key
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                self.s3.download_file(self.bucket, key, str(local_path))
                
                progress = (i + 1) / len(files_to_download)
                progress_bar.progress(progress)
                status_text.text(f'Downloading telemetry data: {i + 1}/{len(files_to_download)} files')
            
            progress_bar.empty()
            status_text.empty()
            
            return True
        except Exception as e:
            st.error(f"Failed to download data: {e}")
            return False
    
    def get_local_data_path(self):
        return self.local_cache
