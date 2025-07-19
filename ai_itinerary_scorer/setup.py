from setuptools import setup, find_packages

setup(
    name="ai_itinerary_scorer",
    version="0.1.0",
    description="AI-powered itinerary analysis and scoring for India travel (PDF, DOCX, text supported).",
    author="Your Name",
    author_email="youremail@example.com",
    url="https://github.com/yourname/ai_itinerary_scorer",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi==0.110.0",
        "uvicorn[standard]==0.29.0",
        "PyPDF2==3.0.1",
        "pdfminer.six==20231228",
        "python-docx==1.1.2",
        "pytesseract==0.3.10",
        "Pillow==10.3.0",
        "PyMuPDF==1.24.4",
        "spacy==3.7.4",
        "scikit-learn==1.4.2",
        "sentence-transformers==2.7.0",
        "faiss-cpu==1.8.0",
        "transformers==4.40.0",
        "sqlite-utils==3.36",
        "pandas==2.2.2",
        "numpy==1.26.4",
        "python-dotenv==1.0.1",
        "pydantic==2.7.3",
        "tqdm==4.66.4"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ai-itinerary-api=src.phase6_deployment.api_server:app",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Typing :: Typed",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
    ],
)
