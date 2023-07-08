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

# until https://bugs.python.org/issue46276 is not fixed we can apply this
# workaround on windows
if os.name == 'nt':
    import win32api

    win32api.LoadLibrary('LocationRotation')

import fastdds
import LocationRotation


class ReaderListener(fastdds.DataReaderListener):
    def __init__(self):
        super().__init__()

    # 加断点不停？
    def on_data_available(self, reader):
        info = fastdds.SampleInfo()
        lRBean = LocationRotation.LocationRotationBean()
        # data = TestDemo.TestDemo()
        reader.take_next_sample(lRBean, info)
        players = lRBean.Players()
        player = players[0]
        # print("Received {message} : {index}".format(message=data.message(), index=data.id()))
        print("Received: {x}".format(x=player.x()))

    def on_subscription_matched(self, datareader, info):
        if (0 < info.current_count_change):
            print("Subscriber matched publisher {}".format(info.last_publication_handle))
        else:
            print("Subscriber unmatched publisher {}".format(info.last_publication_handle))


class Reader():
    def __init__(self, domain):
        factory = fastdds.DomainParticipantFactory.get_instance()

        self.participant_qos = fastdds.DomainParticipantQos()
        factory.get_default_participant_qos(self.participant_qos)
        self.participant = factory.create_participant(domain, self.participant_qos)
        # self.participant = factory.create_participant_with_profile('participant_profile')

        # self.topic_data_type = TestDemo.TestDemoPubSubType()
        self.topic_data_type = LocationRotation.LocationRotationBeanPubSubType()
        self.topic_data_type.setName("LocationRotationBean")
        self.type_support = fastdds.TypeSupport(self.topic_data_type)
        self.participant.register_type(self.type_support)

        self.topic_qos = fastdds.TopicQos()
        self.participant.get_default_topic_qos(self.topic_qos)
        self.topic = self.participant.create_topic("myTopic", self.topic_data_type.getName(), self.topic_qos)

        self.subscriber_qos = fastdds.SubscriberQos()
        self.participant.get_default_subscriber_qos(self.subscriber_qos)
        self.subscriber = self.participant.create_subscriber(self.subscriber_qos)

        self.listener = ReaderListener()
        self.reader_qos = fastdds.DataReaderQos()
        self.subscriber.get_default_datareader_qos(self.reader_qos)
        self.reader = self.subscriber.create_datareader(self.topic, self.reader_qos, self.listener)

    def __del__(self):
        factory = fastdds.DomainParticipantFactory.get_instance()
        self.participant.delete_contained_entities()
        factory.delete_participant(self.participant)

    def run(self):
        try:
            input('Press any key to stop\n')
        except:
            pass


if __name__ == '__main__':
    reader = Reader(0)
    reader.run()
