"""
Cloud Storage Adapter
Supports both local file storage and cloud storage (Vercel Blob, AWS S3)
"""
import os
import io
from typing import Optional, Dict, Any, BinaryIO
from fastapi import UploadFile
import aiofiles
from datetime import datetime


class StorageAdapter:
    """Abstract storage adapter interface"""
    
    async def upload_file(self, file: UploadFile, filename: str) -> Dict[str, Any]:
        """Upload a file and return file path/URL and metadata"""
        raise NotImplementedError
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file content as bytes"""
        raise NotImplementedError
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        raise NotImplementedError
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        raise NotImplementedError


class LocalStorageAdapter(StorageAdapter):
    """Local filesystem storage adapter"""
    
    def __init__(self, upload_dir: str = "./uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    async def upload_file(self, file: UploadFile, filename: str) -> Dict[str, Any]:
        """Upload file to local filesystem"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
            await file.seek(0)  # Reset file pointer for later use
        
        return {
            "file_path": file_path,
            "url": file_path,
            "filename": unique_filename,
            "storage_type": "local"
        }
    
    async def download_file(self, file_path: str) -> bytes:
        """Read file from local filesystem"""
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists locally"""
        return os.path.exists(file_path)
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from local filesystem"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False


class VercelBlobStorageAdapter(StorageAdapter):
    """Vercel Blob Storage adapter"""
    
    def __init__(self):
        try:
            from vercel_blob import put, head, del_blob
            self.put = put
            self.head = head
            self.del_blob = del_blob
        except ImportError:
            raise ImportError("vercel-blob package not installed. Install with: pip install vercel-blob")
    
    async def upload_file(self, file: UploadFile, filename: str) -> Dict[str, Any]:
        """Upload file to Vercel Blob Storage"""
        content = await file.read()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        
        blob = await self.put(
            unique_filename,
            content,
            {
                "contentType": file.content_type or "application/octet-stream",
                "addRandomSuffix": True
            }
        )
        
        return {
            "file_path": blob.url,
            "url": blob.url,
            "filename": unique_filename,
            "storage_type": "vercel_blob",
            "blob_id": blob.url
        }
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from Vercel Blob"""
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(file_path)
            response.raise_for_status()
            return response.content
    
    def file_exists(self, file_path: str) -> bool:
        """Check if blob exists (synchronous check)"""
        # Vercel Blob doesn't have a synchronous head, so we'll try to download
        # In production, you might want to cache this
        return True  # Assume exists if URL is provided
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete blob from Vercel Blob Storage"""
        try:
            # Extract blob path from URL
            blob_path = file_path.split('/')[-1]
            await self.del_blob(blob_path)
            return True
        except Exception:
            return False


class S3StorageAdapter(StorageAdapter):
    """AWS S3 Storage adapter"""
    
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        try:
            import boto3
            from botocore.exceptions import ClientError
            self.s3_client = boto3.client('s3', region_name=region)
            self.bucket_name = bucket_name
            self.ClientError = ClientError
        except ImportError:
            raise ImportError("boto3 package not installed. Install with: pip install boto3")
    
    async def upload_file(self, file: UploadFile, filename: str) -> Dict[str, Any]:
        """Upload file to S3"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        s3_key = f"uploads/{unique_filename}"
        
        content = await file.read()
        
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=content,
            ContentType=file.content_type or "application/octet-stream"
        )
        
        url = f"https://{self.bucket_name}.s3.{self.s3_client.meta.region_name}.amazonaws.com/{s3_key}"
        
        return {
            "file_path": s3_key,
            "url": url,
            "filename": unique_filename,
            "storage_type": "s3"
        }
    
    async def download_file(self, file_path: str) -> bytes:
        """Download file from S3"""
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_path)
        return response['Body'].read()
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except self.ClientError:
            return False
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except Exception:
            return False


def get_storage_adapter() -> StorageAdapter:
    """
    Factory function to get the appropriate storage adapter based on environment variables.
    Priority: VERCEL_BLOB > AWS_S3 > Local
    """
    # Check for Vercel Blob
    if os.getenv("VERCEL_BLOB_STORAGE") == "true" or os.getenv("BLOB_READ_WRITE_TOKEN"):
        try:
            return VercelBlobStorageAdapter()
        except ImportError:
            pass
    
    # Check for AWS S3
    if os.getenv("AWS_S3_BUCKET"):
        bucket = os.getenv("AWS_S3_BUCKET")
        region = os.getenv("AWS_REGION", "us-east-1")
        try:
            return S3StorageAdapter(bucket_name=bucket, region=region)
        except ImportError:
            pass
    
    # Default to local storage
    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    return LocalStorageAdapter(upload_dir=upload_dir)

