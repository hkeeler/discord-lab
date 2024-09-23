FROM public.ecr.aws/lambda/python:3.12

WORKDIR $LAMBDA_TASK_ROOT

RUN pip install poetry

COPY src poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-cache

CMD [ "discord_lab.interactions.aws_lambda.handler" ]