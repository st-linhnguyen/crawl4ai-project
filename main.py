import logging
from fastapi import FastAPI
import inngest
import inngest.fast_api
import asyncio
from crawler import start_crawl

# Create an Inngest client
inngest_client = inngest.Inngest(
  app_id="fast_api_example",
  logger=logging.getLogger("uvicorn"),
)

# Create an Inngest function
@inngest_client.create_function(
  fn_id="my_function",
  # Event that triggers this function
  trigger=inngest.TriggerEvent(event="app/my_function"),
)

async def my_function(ctx: inngest.Context, step: inngest.Step) -> str:
  ctx.logger.info(ctx.event)
  urls = ctx.event.data['urls']
  extracted_data = await start_crawl(urls)
  # print(extracted_data)
  jobs = extracted_data[0].jobs
  result = [job.model_dump_json() for job in jobs]
  print(result)
  return result

  # return "done 12313"

app = FastAPI()

# Serve the Inngest endpoint
inngest.fast_api.serve(app, inngest_client, [my_function])
