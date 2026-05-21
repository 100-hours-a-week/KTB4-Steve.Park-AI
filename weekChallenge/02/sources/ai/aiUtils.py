from openai import AsyncOpenAI
from utils.models import ResponseEntity, ReturnFlag as RF
from db import postsdb

client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

async def getGemmaPostSummary(idx: int) -> ResponseEntity:
    msg = ResponseEntity()

    board = await postsdb.getBoardDetail(idx)
    if board.error_code != RF.Success.value:
        msg.error_code = board.error_code
        msg.msg = board.msg
        return msg
    
    boarddetail = board.res
    title = boarddetail.title
    contents = boarddetail.contents

    responses_result = await client.chat.completions.create(
        model="gemma4:e2b",
        messages=[{"role": "user", "content": f"Please summarize the following post in 3 sentences or less.\n\nTitle: {title}\nContents: {contents}."
                   + " Also you have to summarize the title and contents into specific language, which mostly used in the contents"}]
    )

    msg.res = responses_result.choices[0].message.content
    return msg

async def getGemmaPostCommentSummary(idx: int) -> ResponseEntity:
    msg = ResponseEntity()

    board = await postsdb.getBoardDetail(idx)
    if board.error_code != RF.Success.value:
        msg.error_code = board.error_code
        msg.msg = board.msg
        return msg
    
    comments_result = await postsdb.getBoardComments(idx)
    comments = comments_result.res or []

    if not comments:
        msg.error_code = RF.BoardCommentNotExist.value
        msg.msg = RF.BoardCommentNotExist.message
        return msg
    
    responses_result = await client.chat.completions.create(
        model="gemma4:e2b",
        messages=[{"role": "user", "content": f"Please summarize the comments of the post where comments are {comments}. "
                   + "you don't have to summarize one by one, just summarize overall comments in 3 sentences or less."
                   + " Also you have to summarize the comments into specific language, which mostly used in the comments"}]
    )

    msg.res = responses_result.choices[0].message.content
    return msg