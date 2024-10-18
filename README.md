# AIM Hackathon Oct 2024 - Template
Repository for the first AIM Hackathon together with TIMETOACT GROUP Österreich on 19.10.2024


## Check out OpenAI pricing 
https://openai.com/api/pricing/


## Set up OpenAI API Key
Copy your teams API key from the [slack](https://join.slack.com/t/aim-ai-impact-mission/shared_invite/zt-2sfahg4h1-Pb7~Ft4ZITZKGAHihEK6QQ)) channel description and place it in the `.env_template` file.

Don't forget to replace the filename to `.env` afterwards!

Check out the sample code to see how to load the key.


## About the data
The dataset [`reports.json`](data/reports.json) contains the following keys:
- `company_name`: name of the company
- `year`: year of the report (if report is for two years, the first year is used)
- `dataset`: subdataset name
    - `scraped`: scraped from a website, might contain broken links and irrelevant pdfs (90 samples, 2016-2024)
    - `austria`: reports from mainly Austrian companies (33 samples)
    - `handcrafted`: selected by hand, ESG and sustainability reports (23 samples, 2019, 2021, 2023 for every company)
- `pdf_url`: link to the pdf report


## Jump start
### Set up environment
Create a new environment (e.g. with conda)
```bash
conda create -n aim_hackathon_oct24 python=3.8
```

Install the requirements
```bash
pip install -r requirements.txt
```


### Sample code
There is a super simple RAG implementation to help getting you started in [`sample_code.ipynb`](sample_code.ipynb).
