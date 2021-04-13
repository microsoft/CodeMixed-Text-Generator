import requests
import zipfile
import os
import subprocess

def install_fast_align():

    # fetch fast_align from github
    url = "https://github.com/clab/fast_align/archive/master.zip"
    print("fetching fast_align from web")
    res = requests.get(url, allow_redirects=True)

    # save the fetched data as a file
    open("master.zip", "wb").write(res.content)
    print("extracting fast_align from downloaded zip file")
    with zipfile.ZipFile("master.zip", "r") as zip_ref:
        zip_ref.extractall(".")

    # create build directory
    os.chdir("fast_align-master/")
    os.mkdir("build")
    os.chdir("build")

    # setup make
    print("setting up make")
    p_cmake = subprocess.run(["cmake", ".."], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print((p_cmake.stdout).decode())

    # make to compile fast_align
    print("compiling fast_align")
    print(os.getcwd())
    p_make = subprocess.run(["make"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print((p_make.stdout).decode())

    # get rid of extra files
    print("fast_align is successfully installed. Now cleaning up")
    os.chdir("../../")
    os.remove("master.zip")
    print("Done.")

if __name__ == "__main__":
    try:
        install_fast_align()
    except Exception as err:
        print(err)