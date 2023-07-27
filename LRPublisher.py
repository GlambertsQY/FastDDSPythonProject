#!/usr/bin/env python3
# # Copyright 2021 Proyectos y Sistemas de Mantenimiento SL (eProsima).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Script to test Fast DDS python bindings
"""
import os
import time
from threading import Condition

# until https://bugs.python.org/issue46276 is not fixed we can apply this
# workaround on windows
if os.name == 'nt':
    import win32api

    win32api.LoadLibrary('FastDDSJsonStr')

import fastdds
import FastDDSJsonStr


class WriterListener(fastdds.DataWriterListener):
    def __init__(self, writer):
        self._writer = writer
        super().__init__()

    # 重写callback on_publication_matched()
    # 用来定义当一个新的DataReader被检测到正在监听此publisher的topic时的一系列动作。
    # info.current_count_change()检测此DataWriter对应的DataReaders的状态变化。
    # 如果有新的match的DataReader就打印Publisher matched。
    # unmatch意思是断开了和某个DataReader的关联
    def on_publication_matched(self, datawriter, info):
        if (0 < info.current_count_change):
            print("Publisher matched subscriber {}".format(info.last_subscription_handle))
            self._writer._cvDiscovery.acquire()
            self._writer._matched_reader += 1
            self._writer._cvDiscovery.notify()
            self._writer._cvDiscovery.release()
        else:
            print("Publisher unmatched subscriber {}".format(info.last_subscription_handle))
            self._writer._cvDiscovery.acquire()
            self._writer._matched_reader += 1
            self._writer._cvDiscovery.notify()
            self._writer._cvDiscovery.release()


class Writer:
    def __init__(self, domain, machine, topic_name):
        self.machine = machine
        self._matched_reader = 0
        self._cvDiscovery = Condition()

        factory = fastdds.DomainParticipantFactory.get_instance()

        self.participant_qos = fastdds.DomainParticipantQos()
        factory.get_default_participant_qos(self.participant_qos)
        self.participant = factory.create_participant(domain, self.participant_qos)


        self.topic_data_type = FastDDSJsonStr.JsonStrBeanPubSubType()
        self.topic_data_type.setName("JsonStrBean")
        self.type_support = fastdds.TypeSupport(self.topic_data_type)
        self.participant.register_type(self.type_support)

        self.topic_qos = fastdds.TopicQos()
        self.topic_qos.history = fastdds.KEEP_ALL_HISTORY_QOS
        self.topic_qos.deadline = 1000000
        self.participant.get_default_topic_qos(self.topic_qos)
        self.topic = self.participant.create_topic(topic_name, self.topic_data_type.getName(), self.topic_qos)

        self.publisher_qos = fastdds.PublisherQos()
        self.participant.get_default_publisher_qos(self.publisher_qos)
        self.publisher = self.participant.create_publisher(self.publisher_qos)

        self.listener = WriterListener(self)
        self.writer_qos = fastdds.DataWriterQos()
        self.publisher.get_default_datawriter_qos(self.writer_qos)
        self.writer = self.publisher.create_datawriter(self.topic, self.writer_qos, self.listener)

        self.index = 0

    def write(self):
        sendStr = FastDDSJsonStr.JsonStrBean()
        # data = TestDemo.TestDemo()
        sendStr.JsonString("qwe23[]f")

        # if self.machine:
        #     players.message("TestDemo " + self.machine)
        # else:
        #     players.message("TestDemo")
        self.writer.write(sendStr)
        # print("Sending {message} : {index}".format(message=players.message(), index=players.id()))
        print("Sending success!")

    def __del__(self):
        factory = fastdds.DomainParticipantFactory.get_instance()
        self.participant.delete_contained_entities()
        factory.delete_participant(self.participant)

    def run(self):
        self.wait_discovery()
        self.write()

    def wait_discovery(self):
        self._cvDiscovery.acquire()
        print("Writer is waiting discovery...")
        self._cvDiscovery.wait_for(lambda: self._matched_reader != 0)
        self._cvDiscovery.release()
        print("Writer discovery finished...")


if __name__ == '__main__':
    print('Creating publisher.')
    writer = Writer(0, 'tester01', 'myTopic')
    while True:
        writer.run()
        time.sleep(0.5)
