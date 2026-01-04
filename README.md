# HuggingFace Daily Papers Abstracts Extractor

This project automates the process of downloading, summarizing, and converting daily papers from Hugging Face into easily readable formats.

![Sample output of abstract extraction process](img/daily_hf_papers_abstracts_sample_output.png)

## Features

- Download daily papers from Hugging Face API
- Extract abstracts and generate markdown summaries
- Handle empty files and weekends/holidays
- Avoid reprocessing existing files

## Project Structure

```
hf_daily_papers/
│
├── data/
│   ├── input/  # Downloaded JSON files
│   ├── output/ # Generated markdown files
│
├── src/
│   ├── download_daily_papers.py
│   ├── daily_papers_abstract_extractor.py
│
└── README.md
```

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/xieyuquanxx/get_hf_daily_paper.git
   cd get_hf_daily_paper
   ```

2. Install the required dependencies:

   ```
   pip install requests
   ```

## Usage

```
bash get_daily_paper.sh YYYYMMDD-YYYYMMDD # such as bash get_daily_paper.sh 20251201-20260101
```
If no date is provided, it will download papers for the current date.



## Notes

- The scripts handle empty files that may occur during weekends or holidays.
- Existing processed files are not overwritten to avoid unnecessary reprocessing.
- You can run these scripts daily to keep up with the latest papers.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](https://choosealicense.com/licenses/mit/).
