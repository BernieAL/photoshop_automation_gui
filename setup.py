from setuptools import setup

setup(
    name="photoshop-automation",
    version="1.0",
    packages=["Photoshop_scripts"],
    install_requires=[
        "photoshop-python-api",
        # other dependencies
    ],
    entry_points={
        "console_scripts": [
            "watermark=Photoshop_scripts.ps_scripts.single_folder_watermarking_only_script:main",
        ],
    }
) 