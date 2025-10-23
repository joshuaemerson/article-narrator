# article-narrator
This project leverages AWS Polly to narrate user supplied articles. The article is supplied via a URL and
its contents are stored as text and then transformed into speech using AWS Polly. The resulsting .mp3 file
is stored in S3 for future listening.

# How to use
```
python3 main.py <URL>
```

# Sample Output
[Why_has_the_US_imposed_sanctions_on_Russian_oil_companies.mp3](https://github.com/user-attachments/files/23103171/Why_has_the_US_imposed_sanctions_on_Russian_oil_companies.mp3)
