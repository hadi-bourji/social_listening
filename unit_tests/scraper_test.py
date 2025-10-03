import pytest
from social_listening.utils.web_scraper import pacelabs_scraper, epa_scraper, sgs_scraper, montrose_scraper, gel_scraper, emsl_scraper, babcock_scraper, wecklabs_scraper, alsglobal_scraper, microbac_scraper

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

