import pytest
import re
import pytz
from datetime import datetime
from utils.web_scraper import pacelabs_scraper, epa_scraper, sgs_scraper, montrose_scraper, gel_scraper, emsl_scraper, babcock_scraper, wecklabs_scraper, alsglobal_scraper, microbac_scraper
from utils.articles import replace_tag_with_boundary, remove_exact_duplicates_and_international, convert_article_to_central, convert_articles_to_central, get_relevant_articles

# Run with python -m pytest unit_tests/function_test.py from social_listening directory

scrapers = [pacelabs_scraper, epa_scraper, sgs_scraper, montrose_scraper, gel_scraper, emsl_scraper, babcock_scraper, wecklabs_scraper, alsglobal_scraper, microbac_scraper]

@pytest.mark.parametrize("scraper_func", scrapers)
def test_scraper_structure(scraper_func):
    articles = scraper_func()
    assert isinstance(articles, list)
    assert all(isinstance(article, dict) for article in articles)
    for article in articles:
        assert "title" in article
        assert "date" in article
        assert "description" in article
        assert "url" in article
        
def test_replace_tag_with_boundary():
    text = "This is a sentence.</p> Next one."

    match = re.search(r'(</p>|<br\s*/?>|</div>)', text)
    assert match is not None

    result = replace_tag_with_boundary(match, text)
    assert result == " "


    text = "This is a sentence</p> Next one."
    
    match = re.search(r'(</p>|<br\s*/?>|</div>)', text)
    assert match is not None

    result = replace_tag_with_boundary(match, text)
    assert result == ". "    

def test_remove_exact_duplicates_and_international():
    d = {1:{
                'Article Title': 'title',
                'Article Link': 'link',
                'Date and Time Published': 'date',
                'Matched Keywords': 'matched_keywords',
                'Context': 'spain is a country'
            },
            2:{
                'Article Title': 'title',
                'Article Link': 'link',
                'Date and Time Published': 'date',
                'Matched Keywords': 'matched_keywords',
                'Context': 'no international countries here!'
            }}
    result = remove_exact_duplicates_and_international(d)
    assert result == {1:{
                'Article Title': 'title',
                'Article Link': 'link',
                'Date and Time Published': 'date',
                'Matched Keywords': 'matched_keywords',
                'Context': 'no international countries here!'
            }}
    

def test_convert_article_with_timezone():
    #case where article contains date
    article = {"Date and Time Published": "2025-10-03 14:30:00 EST"}
    result = convert_article_to_central(article)

    assert "datetime_obj" in result
    dt = result["datetime_obj"]
    assert isinstance(dt, datetime)

    assert dt.tzinfo.zone in ("America/Chicago",)  


    #case where article does not contain date
    article = {"Title": "No date case"}
    result = convert_article_to_central(article)

    assert result["datetime_obj"] == datetime.min
    assert result["readable_time"] == "Published Date not Provided in RSS Feed"


    #case with multiple articles
    articles = {1: {"Date and Time Published": "2025-10-03 08:00:00 PST"},
        2: {"Date and Time Published": "2025-10-03 10:00:00 EST"},}
    results = convert_articles_to_central(articles)

    assert isinstance(results, dict)
    assert len(results) == 2
    for article in results.values():
        assert "datetime_obj" in article
        assert "readable_time" in article