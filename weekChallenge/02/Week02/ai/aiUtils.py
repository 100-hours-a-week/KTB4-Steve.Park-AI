from openai import AsyncOpenAI
from utils.models import ResponseEntity, ReturnFlag as RF
from db import boarddb

client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

async def getGemmaPostSummary(idx: int) -> ResponseEntity:
    msg = ResponseEntity()

    board = await boarddb.getBoardDetail(idx)
    if board.flag != RF.Success.value:
        msg.flag = board.flag
        msg.msg = board.msg
        return msg
    
    boarddetail = board.res
    title = boarddetail.title
    contents = boarddetail.contents

    responses_result = await client.chat.completions.create(
        model="gemma4:e2b",
        messages=[{"role": "user", "content": f"Please summarize the following post in 3 sentences or less.\n\nTitle: {title}\nContents: {contents}"}]
    )

    msg.res = responses_result.choices[0].message.content
    return msg

async def getGemmaPostCommentSummary(idx: int) -> ResponseEntity:
    msg = ResponseEntity()

    board = await boarddb.getBoardDetail(idx)
    if board.flag != RF.Success.value:
        msg.flag = board.flag
        msg.msg = board.msg
        return msg
    
    comments_result = await boarddb.getBoardComments(idx)
    comments = comments_result.res or []

    if not comments:
        msg.flag = RF.BoardCommentNotExist.value
        msg.msg = RF.BoardCommentNotExist.name
        return msg
    
    responses_result = await client.chat.completions.create(
        model="gemma4:e2b",
        messages=[{"role": "user", "content": f"Please summarize the comments of the post where comments are {comments}. you don't have to summarize one by one, just summarize overall comments in 3 sentences or less."}]
    )

    msg.res = responses_result.choices[0].message.content
    return msg