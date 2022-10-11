import re

# Regular expressions
re_punct      = re.compile(r"[\-+/|]")
re_alpha      = re.compile(r"[^a-z \.]+")
re_alphanum   = re.compile(r"[^a-z0-9 \.]+")
re_newline    = re.compile(r"([A-Za-z0-9]{2})\. ")
re_zipcode    = re.compile(r"(?:^|\D)(\d{5}(?:-\d{4})?)(?:\D|$)")
re_year       = re.compile(r"(?:^|\D)(\d{4})(?:\D|$)")
re_date_range = re.compile(r"|".join((
    r"(?P<fmonth>\w+.\d+)\s*(?:-|to)\s*(?P<smonth>\w+.\d+|present|current)",
    r"(\d{4})\s*(?:-|to)\s*(\d{4}|present|current)",
    r"(\d{1,2}/\d{4})\s*(?:-|to)\s*(\d{1,2}/\d{4}|present|current)"
)))
re_dollar_with_commas = re.compile(r"\$(0|[1-9][0-9]{0,2})(,\d{3})*(\.\d{1,2})?$")
re_dollar_wo_commas = re.compile(r"\$(0|[1-9][0-9]{0,2})(\d{3})*(\.\d{1,2})?$")

re_year_month = [
    (re.compile(r"(?:^|\D)(\d{4}-\d{2})(?:\D|$)"), lambda x: x),
    (re.compile(r"(?:^|\D)(\d{4}/\d{2})(?:\D|$)"), lambda x: x.replace("/", "-")),
    (re.compile(r"(?:^|\D)(\d{1,2}/\d{4})(?:\D|$)"), lambda x: x[-4:] + "-" + x[:-4].zfill(2)),
    (re.compile(r"jan(?:uary)? (\d{4})"),   lambda x: x + "-01"),
    (re.compile(r"feb(?:ruary)? (\d{4})"),  lambda x: x + "-02"),
    (re.compile(r"mar(?:ch)? (\d{4})"),     lambda x: x + "-03"),
    (re.compile(r"apr(?:ril)? (\d{4})"),    lambda x: x + "-04"),
    (re.compile(r"may (\d{4})"),            lambda x: x + "-05"),
    (re.compile(r"jun(?:e)? (\d{4})"),      lambda x: x + "-06"),
    (re.compile(r"jul(?:y)? (\d{4})"),      lambda x: x + "-07"),
    (re.compile(r"aug(?:ust)? (\d{4})"),    lambda x: x + "-08"),
    (re.compile(r"sep(?:tember)? (\d{4})"), lambda x: x + "-09"),
    (re.compile(r"oct(?:ober)? (\d{4})"),   lambda x: x + "-10"),
    (re.compile(r"nov(?:ember)? (\d{4})"),  lambda x: x + "-11"),
    (re.compile(r"dec(?:ember)? (\d{4})"),  lambda x: x + "-12"),
]