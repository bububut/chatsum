from datetime import datetime, timedelta
import logging
import clickhouse_driver

from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.text_splitter import CharacterTextSplitter

from config import config


logger = logging.getLogger('chat_summary')

def do_summary(room_id, hour):
    chclient = clickhouse_driver.Client(
        'localhost', port=config['clickhouse_port'],
        user=config['clickhouse_user'], password=config['clickhouse_password'])
    fromdt = datetime.now().replace(hour=hour, second=0, minute=0, microsecond=0) - timedelta(days=1)
    sql = f"select * from chat_history where room_id = '{room_id}' and dt >= '{fromdt}'"
    # print(sql)
    res = chclient.execute(sql)
    lines = []
    for dt, _, name, _, _, text, q_name, q_text in res:
        if len(q_text) > 0:
            text = f'{text} @{q_name}:{q_text}'
        text = text.replace('\n', '\t')
        line = f'{dt}|{name}|{text}'
        lines.append(line)
    fulldoc = '\n'.join(lines)

    # split fulldoc
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(        
        separator = "\n",
        chunk_size = 5000,
        chunk_overlap  = 200,
        model_name='gpt-4'
    )
    texts = text_splitter.split_text(fulldoc)

    prompt = '''
        The following text delimieted by triple backtick is a chat record.
        Each line represents one message, the format is:
        Date | Speaker | Content
        Please summarize the topics that are of interest to everyone and discussed more in this text (over 10 messages, over two people communicating), and rank them by popularity from 10 points to 1 point.
        Each topic summary contains 4 parts:
        `Date Time`: The date and time the topic started, format `2021-05-09 10:00:00`
        `Topic popularity`: Evaluate the total number of related speeches and number of participants, with numbers 1-10, the hottest topic is 10
        `Topic mood`: The overall mood of the speeches in the topic, expressed with an emoji, e.g. 😐 😀 😂 🤑 😍 😈 👽
        `Topic summary`: Summarize the main content of the topic in your own words, do not use the original text, no more than 50 words
        `Opinions and discussions`: Under each topic, summarize the core content and ideas of the main participants. Summarize the speeches of the same participant under the same topic into one, and participants cannot appear repeatedly. Use line breaks `\n` to separate different participants. If there is a URL, it must be attached.

        Output format:
        `Date Time` Popularity:`Topic Popularity` Mood:`Topic mood`\n 【`Topic summary`】\n`Opinions and discussions`\n

        ```
        {text}
        ```
    '''

    chat = ChatAnthropic(model='claude-v1.3', max_tokens_to_sample=1000, temperature=0.5)
    chatreslist = []
    for text in texts:
        final_prompt = prompt.format(text=text)
        messages = [
            SystemMessage(content="You are a helpful assistant that can summarize chat history in Chinese."),
            HumanMessage(content=final_prompt)
        ]
        chatres = chat.generate([messages])
        chatreslist.append(chatres)


    smry0 = '\n\n'.join([chatres.generations[0][0].text for chatres in chatreslist])
    smry = f'*** {datetime.now().date()} Chat Summary ***\n\n' + smry0
    return smry

if __name__ == '__main__':
    do_summary('sample_id')
