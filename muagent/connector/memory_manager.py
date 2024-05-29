from abc import abstractmethod, ABC
from typing import List, Dict
import os, sys, copy, json, uuid
from jieba.analyse import extract_tags
from collections import Counter
from loguru import logger
import numpy as np

from langchain.docstore.document import Document


from .schema import Memory, Message
from muagent.service.service_factory import KBServiceFactory
from muagent.llm_models import getChatModelFromConfig
from muagent.llm_models.llm_config import EmbedConfig, LLMConfig
from muagent.embeddings.utils import load_embeddings_from_path
from muagent.utils.common_utils import *
from muagent.connector.configs.prompts import CONV_SUMMARY_PROMPT_SPEC
from muagent.orm import table_init
from muagent.base_configs.env_config import KB_ROOT_PATH
# from configs.model_config import KB_ROOT_PATH, EMBEDDING_MODEL, EMBEDDING_DEVICE, SCORE_THRESHOLD
# from configs.model_config import embedding_model_dict


class BaseMemoryManager(ABC):
    """
    This class represents a local memory manager that inherits from BaseMemoryManager.

    Attributes:
    - user_name: A string representing the user name. Default is "default".
    - unique_name: A string representing the unique name. Default is "default".
    - memory_type: A string representing the memory type. Default is "recall".
    - do_init: A boolean indicating whether to initialize. Default is False.
    - current_memory: An instance of Memory class representing the current memory.
    - recall_memory: An instance of Memory class representing the recall memory.
    - summary_memory: An instance of Memory class representing the summary memory.
    - save_message_keys: A list of strings representing the keys for saving messages.

    Methods:
    - __init__: Initializes the LocalMemoryManager with the given user_name, unique_name, memory_type, and do_init.
    - init_vb: Initializes the vb.
    - append: Appends a message to the recall memory, current memory, and summary memory.
    - extend: Extends the recall memory, current memory, and summary memory.
    - save: Saves the memory to the specified directory.
    - load: Loads the memory from the specified directory and returns a Memory instance.
    - save_new_to_vs: Saves new messages to the vector space.
    - save_to_vs: Saves the memory to the vector space.
    - router_retrieval: Routes the retrieval based on the retrieval type.
    - embedding_retrieval: Retrieves messages based on embedding.
    - text_retrieval: Retrieves messages based on text.
    - datetime_retrieval: Retrieves messages based on datetime.
    - recursive_summary: Performs recursive summarization of messages.
    """
    
    def __init__(
            self,
            user_name: str = "default",
            unique_name: str = "default",
            memory_type: str = "recall",
            do_init: bool = False,
        ):
        """
        Initializes the LocalMemoryManager with the given parameters.

        Args:
        - user_name: A string representing the user name. Default is "default".
        - unique_name: A string representing the unique name. Default is "default".
        - memory_type: A string representing the memory type. Default is "recall".
        - do_init: A boolean indicating whether to initialize. Default is False.
        """
        self.user_name = user_name
        self.unique_name = unique_name
        self.memory_type = memory_type
        self.do_init = do_init
        # self.current_memory = Memory(messages=[])
        # self.recall_memory = Memory(messages=[])
        # self.summary_memory = Memory(messages=[])
        self.current_memory_dict: Dict[str, Memory] = {}
        self.recall_memory_dict: Dict[str, Memory] = {}
        self.summary_memory_dict: Dict[str, Memory] = {}
        self.save_message_keys = [
            'chat_index', 'role_name', 'role_type', 'role_prompt', 'input_query',
            'datetime', 'role_content', 'step_content', 'parsed_output', 'spec_parsed_output', 'parsed_output_list', 
            'task', 'db_docs', 'code_docs', 'search_docs', 'phase_name', 'chain_name', 'customed_kargs']
        self.init_vb()

    def re_init(self, do_init: bool=False):
        self.init_vb()

    def init_vb(self, do_init: bool=None):
        """
        Initializes the vb.
        """
        pass

    def append(self, message: Message):
        """
        Appends a message to the recall memory, current memory, and summary memory.

        Args:
        - message: An instance of Message class representing the message to be appended.
        """
        pass

    def extend(self, memory: Memory):
        """
        Extends the recall memory, current memory, and summary memory.

        Args:
        - memory: An instance of Memory class representing the memory to be extended.
        """
        pass

    def save(self, save_dir: str = ""):
        """
        Saves the memory to the specified directory.

        Args:
        - save_dir: A string representing the directory to save the memory. Default is KB_ROOT_PATH.
        """
        pass

    def load(self, load_dir: str = "") -> Memory:
        """
        Loads the memory from the specified directory and returns a Memory instance.

        Args:
        - load_dir: A string representing the directory to load the memory from. Default is KB_ROOT_PATH.

        Returns:
        - An instance of Memory class representing the loaded memory.
        """
        pass

    def get_memory_pool(self, chat_index: str):
        """
        return memory_pool
        """
        pass

    def router_retrieval(self, text: str=None, datetime: str = None, n=5, top_k=5, retrieval_type: str = "embedding", **kwargs) -> List[Message]:
        """
        Routes the retrieval based on the retrieval type.

        Args:
        - text: A string representing the text for retrieval. Default is None.
        - datetime: A string representing the datetime for retrieval. Default is None.
        - n: An integer representing the number of messages. Default is 5.
        - top_k: An integer representing the top k messages. Default is 5.
        - retrieval_type: A string representing the retrieval type. Default is "embedding".
        - **kwargs: Additional keyword arguments for retrieval.

        Returns:
        - A list of Message instances representing the retrieved messages.
        """
        pass

    def embedding_retrieval(self, text: str, embed_model="", top_k=1, score_threshold=1.0, **kwargs) -> List[Message]:
        """
        Retrieves messages based on embedding.

        Args:
        - text: A string representing the text for retrieval.
        - embed_model: A string representing the embedding model. Default is EMBEDDING_MODEL.
        - top_k: An integer representing the top k messages. Default is 1.
        - score_threshold: A float representing the score threshold. Default is SCORE_THRESHOLD.
        - **kwargs: Additional keyword arguments for retrieval.

        Returns:
        - A list of Message instances representing the retrieved messages.
        """
        pass

    def text_retrieval(self, text: str, **kwargs) -> List[Message]:
        """
        Retrieves messages based on text.

        Args:
        - text: A string representing the text for retrieval.
        - **kwargs: Additional keyword arguments for retrieval.

        Returns:
        - A list of Message instances representing the retrieved messages.
        """
        pass

    def datetime_retrieval(self, datetime: str, text: str = None, n: int = 5, **kwargs) -> List[Message]:
        """
        Retrieves messages based on datetime.

        Args:
        - datetime: A string representing the datetime for retrieval.
        - text: A string representing the text for retrieval. Default is None.
        - n: An integer representing the number of messages. Default is 5.
        - **kwargs: Additional keyword arguments for retrieval.

        Returns:
        - A list of Message instances representing the retrieved messages.
        """
        pass

    def recursive_summary(self, messages: List[Message], split_n: int = 20) -> List[Message]:
        """
        Performs recursive summarization of messages.

        Args:
        - messages: A list of Message instances representing the messages to be summarized.
        - split_n: An integer representing the split n. Default is 20.

        Returns:
        - A list of Message instances representing the summarized messages.
        """
        pass


class LocalMemoryManager(BaseMemoryManager):

    def __init__(
            self,
            embed_config: EmbedConfig,
            llm_config: LLMConfig,
            user_name: str = "default",
            unique_name: str = "default",
            memory_type: str = "recall",
            do_init: bool = False,
            kb_root_path: str = KB_ROOT_PATH,
        ):
        self.user_name = user_name
        self.unique_name = unique_name
        self.memory_type = memory_type
        self.chat_index: str = "default"
        self.do_init = do_init
        self.kb_root_path = kb_root_path
        self.embed_config: EmbedConfig = embed_config
        self.llm_config: LLMConfig = llm_config
        # self.current_memory = Memory(messages=[])
        # self.recall_memory = Memory(messages=[])
        # self.summary_memory = Memory(messages=[])
        self.current_memory_dict: Dict[str, Memory] = {}
        self.recall_memory_dict: Dict[str, Memory] = {}
        self.summary_memory_dict: Dict[str, Memory] = {}
        self.save_message_keys = [
            'chat_index', 'role_name', 'role_type', 'role_prompt', 'input_query',
            'datetime', 'role_content', 'step_content', 'parsed_output', 'spec_parsed_output', 'parsed_output_list', 
            'task', 'db_docs', 'code_docs', 'search_docs', 'phase_name', 'chain_name', 'customed_kargs']
        self.init_vb()

    def re_init(self, do_init: bool=False):
        self.init_vb(do_init)

    def init_vb(self, do_init: bool=None):
        # vb_name = f"{self.user_name}/{self.unique_name}/{self.memory_type}"
        vb_name = f"{self.chat_index}/{self.unique_name}/{self.memory_type}"
        # default to recreate a new vb
        table_init()
        vb = KBServiceFactory.get_service_by_name(vb_name, self.embed_config, self.kb_root_path)
        if vb:
            status = vb.clear_vs()

        check_do_init = do_init if do_init else self.do_init
        if check_do_init:
            self.load(self.kb_root_path, check_do_init)
        else:
            self.load(self.kb_root_path)
            self.save_to_vs()

    def append(self, message: Message) -> None:
        self.check_chat_index(message.chat_index)

        # uuid_name = "_".join([self.user_name, self.unique_name, self.memory_type])
        uuid_name = "_".join([self.chat_index, self.unique_name, self.memory_type])
        datetimes = self.recall_memory_dict[uuid_name].get_datetimes()
        contents = self.recall_memory_dict[uuid_name].get_contents()
        # if message not in chat history, no need to update
        if (message.end_datetime not in datetimes) or ((message.input_query not in contents) and (message.role_content not in contents)):
            self.recall_memory_dict[uuid_name].append(message)
            # 
            if message.role_type == "summary":
                self.summary_memory_dict[uuid_name].append(message)
            else:
                self.current_memory_dict[uuid_name].append(message)

            self.save(self.kb_root_path)
            self.save_new_to_vs([message])

    # def extend(self, memory: Memory):
    #     self.recall_memory.extend(memory)
    #     self.current_memory.extend(self.recall_memory.filter_by_role_type(["summary"]))
    #     self.summary_memory.extend(self.recall_memory.select_by_role_type(["summary"]))
    #     self.save(self.kb_root_path)
    #     self.save_new_to_vs(memory.messages)

    def save(self, save_dir: str = "./"):
        # file_path = os.path.join(save_dir, f"{self.user_name}/{self.unique_name}/{self.memory_type}/converation.jsonl")
        # uuid_name = "_".join([self.chat_index, self.unique_name, self.memory_type])
        file_path = os.path.join(save_dir, f"{self.chat_index}/{self.unique_name}/{self.memory_type}/converation.jsonl")
        uuid_name = "_".join([self.chat_index, self.unique_name, self.memory_type])
        memory_messages = self.recall_memory_dict[uuid_name].dict()
        memory_messages = {k: [
                {kkk: vvv for kkk, vvv in vv.items() if kkk in self.save_message_keys}
                for vv in v ] 
            for k, v in memory_messages.items()
        }
        # 
        save_to_json_file(memory_messages, file_path)

    def load(self, load_dir: str = None, re_init=None) -> Memory:
        load_dir = load_dir or self.kb_root_path
        # file_path = os.path.join(load_dir, f"{self.user_name}/{self.unique_name}/{self.memory_type}/converation.jsonl")
        # uuid_name = "_".join([self.user_name, self.unique_name, self.memory_type])
        file_path = os.path.join(load_dir, f"{self.chat_index}/{self.unique_name}/{self.memory_type}/converation.jsonl")
        uuid_name = "_".join([self.chat_index, self.unique_name, self.memory_type])
        if os.path.exists(file_path) and not re_init:
            recall_memory = Memory(**read_json_file(file_path))
            self.recall_memory_dict[uuid_name] = recall_memory
            self.current_memory_dict[uuid_name] = Memory(messages=recall_memory.filter_by_role_type(["summary"]))
            self.summary_memory_dict[uuid_name] = Memory(messages=recall_memory.select_by_role_type(["summary"]))
        else:
            self.recall_memory_dict[uuid_name] = Memory(messages=[])
            self.current_memory_dict[uuid_name] = Memory(messages=[])
            self.summary_memory_dict[uuid_name] = Memory(messages=[])

    def save_new_to_vs(self, messages: List[Message]):
        if self.embed_config:
            # vb_name = f"{self.user_name}/{self.unique_name}/{self.memory_type}"
            vb_name = f"{self.chat_index}/{self.unique_name}/{self.memory_type}"
            # default to faiss, todo: add new vstype
            vb = KBServiceFactory.get_service(vb_name, "faiss", self.embed_config, self.kb_root_path)
            embeddings = load_embeddings_from_path(self.embed_config.embed_model_path, self.embed_config.model_device, self.embed_config.langchain_embeddings)
            messages = [
                    {k: v for k, v in m.dict().items() if k in self.save_message_keys}
                    for m in messages] 
            docs = [{"page_content": m["step_content"] or m["role_content"] or m["input_query"], "metadata": m} for m in messages]
            docs = [Document(**doc) for doc in docs]
            vb.do_add_doc(docs, embeddings)

    def save_to_vs(self):
        '''only after load'''
        if self.embed_config:
            # vb_name = f"{self.user_name}/{self.unique_name}/{self.memory_type}"
            # uuid_name = "_".join([self.user_name, self.unique_name, self.memory_type])
            vb_name = f"{self.chat_index}/{self.unique_name}/{self.memory_type}"
            uuid_name = "_".join([self.chat_index, self.unique_name, self.memory_type])
            # default to recreate a new vb
            vb = KBServiceFactory.get_service_by_name(vb_name, self.embed_config, self.kb_root_path)
            if vb:
                status = vb.clear_vs()
            # create_kb(vb_name, "faiss", embed_model)

            # default to faiss, todo: add new vstype
            vb = KBServiceFactory.get_service(vb_name, "faiss", self.embed_config, self.kb_root_path)
            embeddings = load_embeddings_from_path(self.embed_config.embed_model_path, self.embed_config.model_device, self.embed_config.langchain_embeddings)
            messages = self.recall_memory_dict[uuid_name].dict()
            messages = [
                    {kkk: vvv for kkk, vvv in vv.items() if kkk in self.save_message_keys}
                    for k, v in messages.items() for vv in v] 
            docs = [{"page_content": m["step_content"] or m["role_content"] or m["input_query"], "metadata": m} for m in messages]
            docs = [Document(**doc) for doc in docs]
            vb.do_add_doc(docs, embeddings)

    # def load_from_vs(self, embed_model=EMBEDDING_MODEL) -> Memory:
    #     vb_name = f"{self.user_name}/{self.unique_name}/{self.memory_type}"

    #     create_kb(vb_name, "faiss", embed_model)
    #     # default to faiss, todo: add new vstype
    #     vb = KBServiceFactory.get_service(vb_name, "faiss", embed_model)
    #     docs =  vb.get_all_documents()
    #     print(docs)

    def get_memory_pool(self, chat_index: str = "") -> Memory:
        self.check_chat_index(chat_index)
        uuid_name = "_".join([self.chat_index, self.unique_name, self.memory_type])
        return self.recall_memory_dict[uuid_name]

    def router_retrieval(self, 
        chat_index: str = "default", text: str=None, datetime: str = None, 
        n=5, top_k=5, retrieval_type: str = "embedding", **kwargs
    ) -> List[Message]:
        retrieval_func_dict = {
            "embedding": self.embedding_retrieval, "text": self.text_retrieval, "datetime": self.datetime_retrieval
            }
        
        # 确保提供了合法的检索类型
        if retrieval_type not in retrieval_func_dict:
            raise ValueError(f"Invalid retrieval_type: '{retrieval_type}'. Available types: {list(retrieval_func_dict.keys())}")

        retrieval_func = retrieval_func_dict[retrieval_type]
        # 
        params = locals()
        params.pop("self")
        params.pop("retrieval_type")
        params.update(params.pop('kwargs', {}))
        # 
        return retrieval_func(**params)

    def embedding_retrieval(self, text: str, top_k=1, score_threshold=1.0, chat_index: str = "default", **kwargs) -> List[Message]:

        if text is None: return []
        vb_name = f"{chat_index}/{self.unique_name}/{self.memory_type}"
        # logger.debug(f"vb_name={vb_name}")
        vb = KBServiceFactory.get_service(vb_name, "faiss", self.embed_config, self.kb_root_path)
        docs = vb.search_docs(text, top_k=top_k, score_threshold=score_threshold)
        return [Message(**doc.metadata) for doc, score in docs]
    
    def text_retrieval(self, text: str, chat_index: str = "default", **kwargs)  -> List[Message]:
        if text is None: return []
        uuid_name = "_".join([chat_index, self.unique_name, self.memory_type])
        # logger.debug(f"uuid_name={uuid_name}")
        return self._text_retrieval_from_cache(self.recall_memory_dict[uuid_name].messages, text, score_threshold=0.3, topK=5, **kwargs)

    def datetime_retrieval(self, chat_index: str, datetime: str, text: str = None, n: int = 5, key: str = "start_datetime", **kwargs) -> List[Message]:
        if datetime is None: return []
        uuid_name = "_".join([chat_index, self.unique_name, self.memory_type])
        # logger.debug(f"uuid_name={uuid_name}")
        return self._datetime_retrieval_from_cache(self.recall_memory_dict[uuid_name].messages, datetime, text, n, **kwargs)
    
    def _text_retrieval_from_cache(self, messages: List[Message], text: str = None, score_threshold=0.3, topK=5, tag_topK=5, **kwargs) -> List[Message]:
        keywords = extract_tags(text, topK=tag_topK)

        matched_messages = []
        for message in messages:
            message_keywords = extract_tags(message.step_content or message.role_content or message.input_query, topK=tag_topK)
            # calculate jaccard similarity
            intersection = Counter(keywords) & Counter(message_keywords)
            union = Counter(keywords) | Counter(message_keywords)
            similarity = sum(intersection.values()) / sum(union.values())
            if similarity >= score_threshold:
                matched_messages.append((message, similarity))
        matched_messages = sorted(matched_messages, key=lambda x:x[1])
        return [m for m, s in matched_messages][:topK]   
     
    def _datetime_retrieval_from_cache(self, messages: List[Message], datetime: str, text: str = None, n: int = 5, **kwargs) -> List[Message]:
        # select message by datetime
        datetime_before, datetime_after = addMinutesToTime(datetime, n)
        select_messages = [
            message for message in messages 
            if datetime_before<=message.end_datetime<=datetime_after
        ]
        return self._text_retrieval_from_cache(select_messages, text)
    
    def recursive_summary(self, messages: List[Message], split_n: int = 20, chat_index: str="") -> List[Message]:

        if len(messages) == 0:
            return messages
        
        newest_messages = messages[-split_n:]
        summary_messages = messages[:len(messages)-split_n]
        
        while (len(newest_messages) != 0) and (newest_messages[0].role_type != "user"):
            message = newest_messages.pop(0)
            summary_messages.append(message)
        
        # summary
        # model = getChatModel(temperature=0.2)
        model = getChatModelFromConfig(self.llm_config)
        summary_content = '\n\n'.join([
            m.role_type + "\n" + "\n".join(([f"*{k}* {v}" for parsed_output in m.parsed_output_list for k, v in parsed_output.items() if k not in ['Action Status']]))
            for m in summary_messages if m.role_type not in  ["summary"]
        ])
        
        summary_prompt = CONV_SUMMARY_PROMPT_SPEC.format(conversation=summary_content)
        content = model.predict(summary_prompt)
        summary_message = Message(
            chat_index=chat_index,
            role_name="summaryer",
            role_type="summary",
            role_content=content,
            step_content=content,
            parsed_output_list=[],
            customed_kargs={}
            )
        summary_message.parsed_output_list.append({"summary": content})
        newest_messages.insert(0, summary_message)
        return newest_messages
    
    def check_chat_index(self, chat_index: str):
        # logger.debug(f"self.user_name is {self.user_name}, self.chat_dex is {self.chat_index}")
        if chat_index != self.chat_index:
            self.chat_index = chat_index
            self.init_vb()

        uuid_name = "_".join([self.chat_index, self.unique_name, self.memory_type])
        if uuid_name not in self.recall_memory_dict:
            self.recall_memory_dict[uuid_name] = Memory(messages=[])
            self.current_memory_dict[uuid_name] = Memory(messages=[])
            self.summary_memory_dict[uuid_name] = Memory(messages=[])

        # logger.debug(f"self.user_name is {self.user_name}")


from muagent.utils.tbase_util import TbaseHandler
from muagent.embeddings.get_embedding import get_embedding
from redis.commands.search.field import (
    TextField,
    NumericField,
    VectorField,
    TagField
)

DIM = 768
MESSAGE_SCHEMA = [
    TextField("chat_index", ),
    TextField("message_index", ),
    TextField("user_name"),
    TextField("role_name",),
    TextField("role_type", ),
    TextField('input_query'),
    TextField("role_content", ),
    TextField("parsed_output"),
    TextField("customed_kargs",),
    TextField("db_docs",),
    TextField("code_docs",),
    TextField("search_docs",),
    NumericField("start_datetime",) ,   
    NumericField("end_datetime",),
    VectorField("vector",
                'FLAT',
                {
                    "TYPE": "FLOAT32",
                    "DIM": DIM,
                    "DISTANCE_METRIC": "COSINE"
                }),
    TagField(name='keyword', separator='|')
]

class TbaseMemoryManager(BaseMemoryManager):

    def __init__(
            self,
            embed_config: EmbedConfig,
            llm_config: LLMConfig,
            user_name: str = "default",
            unique_name: str = "default",
            memory_type: str = "recall",
            do_init: bool = False,
            tbase_handler: TbaseHandler = None,
            use_vector: bool = False,
        ):
        self.user_name = user_name
        self.unique_name = unique_name
        self.memory_type = memory_type
        self.do_init = do_init
        self.embed_config: EmbedConfig = embed_config
        self.llm_config: LLMConfig = llm_config
        self.th: TbaseHandler = tbase_handler
        self.save_message_keys = [
            'chat_index', 'message_index', 'user_name', 'role_name', 'role_type', 'input_query', 'role_content', 'step_content', 
            'parsed_output', 'parsed_output_list', 'customed_kargs', "db_docs", "code_docs", "search_docs", 'start_datetime', 'end_datetime', 
            "keyword", "vector",
        ]
        self.use_vector = use_vector
        self.init_tb()

    def re_init(self, do_init: bool=False):
        self.init_tb(do_init)

    def init_tb(self, do_init: bool=None):
        # create index
        if not self.th.is_index_exists():
            res = self.th.create_index(schema=MESSAGE_SCHEMA)
            logger.info(res)

    def append(self, message: Message) -> None:
        tbase_message = self.localMessage2TbaseMessage(message)
        # logger.debug(f"{type(tbase_message)}\n{tbase_message}")
        self.th.insert_data_hash(tbase_message)

    def extend(self, memory: Memory):
        for message in memory.messages:
            self.append(message)

    def append_tools(self, tool_information: dict, chat_index: str, nodeid: str, user_name: str) -> None:
        '''
        硬编码逻辑不通用
        chat_index: str, 
        nodeid: str, 图谱节点ID
        user_name: str
        tool_information: dict
            - toolKey: str, TOOl的ToolKey
            - toolDef: str, Tool的schema定义
            - toolParam: str, Tool的参数填充结果
            - toolResponse: str, Tool执行的返回值
            - toolSummary: str, Tool的总结结果
        '''
        tool_map = {
             "toolKey": {"role_name": "tool_selector", "role_type": "assistant", "customed_keys": ["toolDef"]}, 
             "toolParam": {"role_name": "tool_filler", "role_type": "assistant"}, 
             "toolResponse": {"role_name": "function_caller", "role_type": "observation"}, 
             "toolSummary": {"role_name": "function_summary", "role_type": "Summary"}, 
        }

        for k, v in tool_map.items():
            try:
                message = Message(
                    chat_index=chat_index,
                    #message_index= f"{nodeid}-{uuid.uuid4()}",
                    message_index= f"{nodeid}-{k}",
                    user_name=user_name,
                    role_name = v["role_name"], # agent 名字，
                    role_type = v["role_type"], # agent 类型，默认assistant，可选observation
                    ## llm output
                    role_content = tool_information[k], # 输入
                    customed_kargs = {
                        **{kk: vv for kk, vv in tool_information.items() 
                            if kk in v.get("customed_keys", [])}
                    } # 存储docs、tool等信息
                )
            except:
                pass
            self.append(message)

    def get_memory_pool(self, chat_index: str = "") -> Memory:
        return self.get_memory_pool_by_all({"chat_index": chat_index})

    def get_memory_pool_by_content(self, content: str, ):
        r = self.th.search(content)
        return self.tbasedoc2Memory(r)

    def get_memory_pool_by_key_content(self, key: str, content: str, ):
        if key == "keyword":
            query = f"@{key}:{{{content}}}"
        else:
            query = f"@{key}:{content}"
        r = self.th.search(content)
        return self.tbasedoc2Memory(r)

    def get_memory_pool_by_all(self, search_key_contents: dict):
        '''
        search_key_contents:
            - key: str, key must in message keys
            - value: str, key' value
        '''
        querys = []
        for k, v in search_key_contents.items():
            if not v: continue
            if k == "keyword":
                querys.append(f"@{k}:{{{v}}}")
            else:
                querys.append(f"@{k}:{v}")
        
        query = f"({')('.join(querys)})" if len(querys) >=2 else "".join(querys)
        r = self.th.search(query)
        return self.tbasedoc2Memory(r)

    def router_retrieval(self, 
        chat_index: str = "default", text: str=None, datetime: str = None, 
        n=5, top_k=5, retrieval_type: str = "embedding", **kwargs
    ) -> List[Message]:

        retrieval_func_dict = {
            "embedding": self.embedding_retrieval, "text": self.text_retrieval, "datetime": self.datetime_retrieval
            }
        
        # 确保提供了合法的检索类型
        if retrieval_type not in retrieval_func_dict:
            raise ValueError(f"Invalid retrieval_type: '{retrieval_type}'. Available types: {list(retrieval_func_dict.keys())}")

        retrieval_func = retrieval_func_dict[retrieval_type]
        # 
        params = locals()
        params.pop("self")
        params.pop("retrieval_type")
        params.update(params.pop('kwargs', {}))
        # 
        return retrieval_func(**params)
        
    def embedding_retrieval(self, text: str, top_k=1, score_threshold=1.0, chat_index: str = "default", **kwargs) -> List[Message]:
        if text is None: return []
        if not self.use_vector and self.embed_config:
            logger.error(f"can't use vector search, because the use_vector is {self.use_vector}")
            return []
        
        if self.use_vector and self.embed_config:
            vector_dict = get_embedding(
                self.embed_config.embed_engine, [text],
                self.embed_config.embed_model_path, self.embed_config.model_device,
                self.embed_config
            )
            query_embedding = np.array(vector_dict[text]).astype(dtype=np.float32).tobytes()
        else:
            query_embedding = np.array([random.random() for _ in range(768)]).astype(dtype=np.float32).tobytes()
        
        base_query = f'(@chat_index:{chat_index})=>[KNN {top_k} @vector $vector AS distance]'
        query_params = {"vector": query_embedding}
        r = self.th.vector_search(base_query, query_params=query_params)
        return self.tbasedoc2Memory(r).messages
    
    def text_retrieval(self, text: str, chat_index: str = "default", **kwargs)  -> List[Message]:
        keywords = extract_tags(text, topK=-1)
        if len(keywords) > 0:
            keyword = "|".join(keywords)
            query = f"(@chat_index:{chat_index})(@keyword:{{{keyword}}})"
        else:
            query = f"@chat_index:{chat_index}"
        # logger.debug(f"text_retrieval query: {query}")
        r = self.th.search(query)
        memory = self.tbasedoc2Memory(r)
        return self._text_retrieval_from_cache(memory.messages, text)

    def datetime_retrieval(self, chat_index: str, datetime: str, text: str = None, n: int = 5, key: str = "start_datetime", **kwargs) -> List[Message]:
        intput_timestamp = datefromatToTimestamp(datetime, 1)
        query = f"(@chat_index:{chat_index})(@{key}:[{intput_timestamp-n*60} {intput_timestamp+n*60}])"
        # logger.debug(f"datetime_retrieval query: {query}")
        r = self.th.search(query)
        memory = self.tbasedoc2Memory(r)
        return self._text_retrieval_from_cache(memory.messages, text)
    
    def _text_retrieval_from_cache(self, messages: List[Message], text: str = None, score_threshold=0.3, topK=5, tag_topK=5, **kwargs) -> List[Message]:
        if text is None:
            return messages[:topK] 

        if len(messages) < topK:
            return messages
        
        keywords = extract_tags(text, topK=tag_topK)

        matched_messages = []
        for message in messages:
            message_keywords = extract_tags(message.step_content or message.role_content or message.input_query, topK=tag_topK)
            # calculate jaccard similarity
            intersection = Counter(keywords) & Counter(message_keywords)
            union = Counter(keywords) | Counter(message_keywords)
            similarity = sum(intersection.values()) / sum(union.values())
            if similarity >= score_threshold:
                matched_messages.append((message, similarity))
        matched_messages = sorted(matched_messages, key=lambda x:x[1])
        return [m for m, s in matched_messages][:topK]   
    
    def recursive_summary(self, messages: List[Message], chat_index: str, message_index: str, user_name: str, split_n: int = 20) -> List[Message]:

        if len(messages) == 0:
            return messages
        
        newest_messages = messages[-split_n:]
        summary_messages = messages[:len(messages)-split_n]
        
        while (len(newest_messages) != 0) and (newest_messages[0].role_type != "user"):
            message = newest_messages.pop(0)
            summary_messages.append(message)
        
        # summary
        model = getChatModelFromConfig(self.llm_config)
        summary_content = '\n\n'.join([
            m.role_type + "\n" + "\n".join(([f"*{k}* {v}" for parsed_output in m.parsed_output_list for k, v in parsed_output.items() if k not in ['Action Status']]))
            for m in summary_messages if m.role_type not in  ["summary"]
        ])
        
        summary_prompt = CONV_SUMMARY_PROMPT_SPEC.format(conversation=summary_content)
        content = model.predict(summary_prompt)
        summary_message = Message(
            chat_index=chat_index,
            message_index=message_index,
            user_name=user_name,
            role_name="summaryer",
            role_type="summary",
            role_content=content,
            step_content=content,
            parsed_output_list=[],
            customed_kargs={}
            )
        summary_message.parsed_output_list.append({"summary": content})
        newest_messages.insert(0, summary_message)
        return newest_messages

    def localMessage2TbaseMessage(self, message: Message):
        '''
        convert Message to redis documents
        '''
        tbase_message = {}
        for k, v in message.dict().items():
            if isinstance(v, dict) or isinstance(v, list):
                v = json.dumps(v, ensure_ascii=False)
            tbase_message[k] = v
        
        # for key in ["db_docs", "code_docs", "search_docs"]:
        #     content = tbase_message.pop(key)
        #     if content is not None:
        #         tbase_message["customed_kargs"][key] = content

        tbase_message["start_datetime"] = datefromatToTimestamp(message.start_datetime, 1)
        tbase_message["end_datetime"] = datefromatToTimestamp(message.end_datetime, 1)

        if self.use_vector and self.embed_config:
            vector_dict = get_embedding(
                self.embed_config.embed_engine, [message.role_content],
                self.embed_config.embed_model_path, self.embed_config.model_device,
                self.embed_config
            )
            tbase_message["vector"] = np.array(vector_dict[message.role_content]).astype(dtype=np.float32).tobytes()
        else:
            tbase_message["vector"] = np.array([random.random() for _ in range(768)]).astype(dtype=np.float32).tobytes()
        tbase_message["keyword"] = " | ".join(extract_tags(message.role_content, topK=-1) 
                                                + [tbase_message["message_index"].split("-")[0]])

        tbase_message = {
            k: v for k, v in tbase_message.items()
            if k in self.save_message_keys
        }
        return tbase_message

    def tbasedoc2Memory(self, r_docs) -> Memory:
        '''
        convert redis documents to Message
        '''
        memory = Memory()
        for doc in r_docs.docs:
            tbase_message = {}
            for k, v in doc.__dict__.items():
                if k in ["role_content", "input_query"]:
                    tbase_message[k] = v
                    continue
                try:
                    v = json.loads(v)
                except:
                    pass

                tbase_message[k] = v

            message = Message(**tbase_message)
            memory.append(message)

        for message in memory.messages:
            message.start_datetime = timestampToDateformat(int(message.start_datetime), 1)
            message.end_datetime = timestampToDateformat(int(message.end_datetime), 1)

        memory.sort_by_key("end_datetime")
        # for message in memory.message:
        #     for key in ["db_docs", "code_docs", "search_docs"]:
        #         content = message.customed_kargs.pop(key)
        #         if content is not None:
        #             message.setattr(key, content)
        return memory