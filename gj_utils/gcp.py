from datetime import datetime
import os
import subprocess
from typing import List

from google.cloud import storage
from IPython.display import clear_output
from tqdm import tqdm


def get_bucket_filenames(bucket_name: str) -> List[str]:
    """Retrieve all filenames in a GCP storage bucket."""
    gcs = storage.Client()
    bucket = gcs.get_bucket(bucket_name)
    blobs = gcs.list_blobs(bucket)
    return [blob.name for blob in tqdm(blobs)]


def mount_bucket(bucket_name: str, localpath: str, implicit_dirs: bool = False):
    """Mount a GCP storage bucket to localpath with gcsfuse."""
    if implicit_dirs:
        result = subprocess.run(["gcsfuse", "--implicit-dirs", bucket_name,
                                 localpath, ], capture_output=True)
    else:
        result = subprocess.run(["gcsfuse", bucket_name, localpath], capture_output=True)
    result_out = result.stdout.decode("utf-8")
    result_err = result.stderr.decode("utf-8").replace("\n", "")
    if result_err != "":
        print(result_err)
        if result_err[-3:] == "EOF":
            print("Bucket already mounted in place?")
    else:
        print(result_out)


def unmount_bucket(directory: str, remove_dir: bool = False):
    """Unmount bucket on linux or mac."""
    try:
        _ = subprocess.run(["fusermount", "-u", str(directory)], capture_output=True)
        print("Unmounted GCP bucket using fusermount")
    except Exception:
        try:
            _ = subprocess.run(["umount", str(directory)], capture_output=True)
            print("Unmounted GCP bucket using umount")
        except Exception:
            print("Unable to un-mount drive")
    if remove_dir:
        os.rmdir(directory)


def copy_between_buckets(src_bucket: str, src_filenames: List[str],
                         dest_bucket: str, dest_filenames: List[str]) -> List[str]:
    """Copy files between source and destination GCP buckets.

    Args:
        src_bucket: name of GCP source bucket to copy files from
        src_filenames: list of filenames to be copied
        dest_bucket: name of GCP destination bucket to receive files
        dest_filenames: list of filenames which src_filenames will be renamed to upon copy

    Returns:
        list of source filenames that were not copied
    """
    timestart = datetime.now()
    missing_files = []
    oneperc = round(len(src_filenames)/100)
    for i in range(len(src_filenames)):
        try:
            cmd_string = "gsutil cp gs://'{}/{}' gs://'{}/{}'".format(src_bucket,
                                                                      src_filenames[i],
                                                                      dest_bucket,
                                                                      dest_filenames[i])
            os.system(cmd_string)
            if i % oneperc == 0:
                timediff = datetime.now() - timestart
                clear_output()
                print("Transfer is {}% complete, "
                      "running for {} mins".format(int(i/oneperc), round(timediff.seconds/60, 2)))
        except Exception:
            print("{} does not exist".format(src_filenames[i]))
            missing_files.append(src_filenames[i])
    return missing_files


def get_file_metadata(gcs: storage.client.Client, bucket_name: str, filename: str) -> str:
    """Retrieve metadata associated with filename on google cloud."""
    bucket_obj = gcs.bucket(bucket_name)
    blob = bucket_obj.get_blob(filename)
    return blob.metadata
