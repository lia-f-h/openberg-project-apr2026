import s3fs
import os
import zipfile
from urllib.parse import urlparse
import tempfile


class BucketParser:
    def __init__(self, url):
        # Initialize the S3 filesystem
        self.s3 = s3fs.S3FileSystem(
            anon=True,
            client_kwargs={
                'endpoint_url': 'https://s3.waw3-1.cloudferro.com'
            }
        )

        # Set the bucket path from the URL
        self.bucket_path = self.get_s3_from_url(url)
        self.items = []  # Initialize items as an empty list     
        self.data_dir='./data'

    # Extract the path from URL and remove the leading slash
    def get_s3_from_url(self, url):
        parsed_url = urlparse(url)
        # Extract the path and remove the leading slash
        bucket_path = parsed_url.path.lstrip('/')
        return bucket_path

    # List content of bucket at a given path (and optionally matching pattern)
    def list_bucket(self, path='', pattern=None):
        # List contents of the bucket at the specified path
        contents = self.s3.ls(f"{self.bucket_path}/{path}")

#        print(f"listing {self.bucket_path}/{path}")
        
        # Sort the contents in alphanumerical order
        sorted_contents = sorted(contents)

        # Clear the items list before populating it
        self.items = []

        for item in sorted_contents:
            # Extract the filename from the item path
            filename = item.split('/')[-1]

            # Check if the pattern is in the filename or if pattern is None
            if pattern is None or (pattern and pattern in filename):
                # Get metadata for each item
                self.items.append(item)
        return self.items

    # Download files from self.items into a specificed data_dir
    def get(self, items=None, data_dir='data'):

        self.files = []

        # Use self.items if no items are provided
        if items is None:
            items = self.items
    
        for item in items:
            zip_filename = os.path.splitext(item.split('/')[-1])[0]
            zip_file_path = os.path.join(tempfile.mkdtemp(), f"{zip_filename}.zip")
        
            # Download the file to /tmp
            self.s3.get(item, zip_file_path)
            print(f"Downloaded: {zip_file_path}")
        
            # Create a 'data' subfolder if it doesn't exist
            self.data_dir=data_dir
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
        
            # Create a subfolder named after the input file (without the .zip extension)
            self.extraction_dir = os.path.join(self.data_dir, zip_filename)
            if not os.path.exists(self.extraction_dir):
                os.makedirs(self.extraction_dir)
        
            # Extract the zip file into the subfolder
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(self.extraction_dir)
        
            print(f"Extracted: {zip_file_path} into {self.extraction_dir}/")

            self.files.append(zip_filename)
            
            # Optionally, remove the zip file after extraction
            os.remove(zip_file_path)
            print(f"Removed: {zip_file_path}")

            return(self.extraction_dir,self.files)
