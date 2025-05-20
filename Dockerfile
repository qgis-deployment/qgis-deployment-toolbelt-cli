FROM python:3.13-slim

# Write .pyc files only once. See: https://stackoverflow.com/a/60797635/2556577
ENV PYTHONDONTWRITEBYTECODE 1
# Make sure that stdout and stderr are not buffered. See: https://stackoverflow.com/a/59812588/2556577
ENV PYTHONUNBUFFERED 1
# Remove assert statements and any code conditional on __debug__. See: https://docs.python.org/3/using/cmdline.html#cmdoption-O
ENV PYTHONOPTIMIZE 2

WORKDIR /user/app

RUN python -m pip install --no-cache-dir -U pip  \
    && python -m pip install --no-cache-dir -U setuptools wheel

COPY . .

RUN python -m pip install -U --no-cache-dir -e .

CMD ["bash"]
