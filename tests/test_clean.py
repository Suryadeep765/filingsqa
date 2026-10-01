from ingest.clean import clean_text


def test_clean_text():
    text = "  $15.0   million\r\n\r\n\r\nCharge  "

    result = clean_text(text)

    assert result == "$15.0 million\n\nCharge"