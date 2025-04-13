from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xiaomi-aiot-edge-security",
    version="0.1.0",
    author="Xiaomi AIoT Security Research Team",
    author_email="example@xiaomi.com",
    description="小米AIoT边缘安全防护研究平台",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xiaomi/aiot-edge-security",
    project_urls={
        "Bug Tracker": "https://github.com/xiaomi/aiot-edge-security/issues",
        "Documentation": "https://github.com/xiaomi/aiot-edge-security/docs",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Internet of Things",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "pyserial>=3.5",
        "edgexfoundry-device-sdk-python>=3.0.0",
        "tb-mqtt-client>=1.5.1",
        "paho-mqtt>=1.6.1",
        "pycryptodome>=3.19.0",
        "cryptography>=41.0.0",
        "pandas>=2.1.0",
        "numpy>=1.26.0",
        "matplotlib>=3.8.0",
        "seaborn>=0.13.0",
        "flask>=2.3.0",
        "flask-socketio>=5.3.0",
        "simpy>=4.0.1",
    ],
    entry_points={
        "console_scripts": [
            "aiot-simulator=src.device_simulator.__main__:main",
            "aiot-security=src.security.__main__:main",
            "aiot-analytics=src.analytics.__main__:main",
            "aiot-dashboard=src.dashboard.app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)