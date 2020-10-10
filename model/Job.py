# State [Done, Unassigned, Assigned]
from datetime import datetime

class Job:
    def __init__(self, chatId, groupType, groupName, msg, frequency):
        self.chatId = chatId
        self.groupType = groupType
        self.groupName = groupName
        self.msg = msg
        self.frequency = frequency
        self.lastSent = -1
        self.created_on = datetime.today()
        self.modifiedOn = datetime.today()

    def set_message(self, msg):
        self.msg = msg
        self.modifiedOn = datetime.today()

    def set_frequency(self, frequency):
        self.frequency = frequency
        self.modifiedOn = datetime.today()

    def toString(self):
        return "ChatId: {} \nGroupName: {} \nMsg: {} \nFrequency: {} seconds \n".format(self.chatId, self.groupName, self.msg
                                                                                        , self.frequency)
    #
    # def toRow(self):
    #     return [self.jobId, self.address, self.note, self.state, self.createdOn, self.modifiedOn, self.assignee]

    # @classmethod
    # def fromRow(cls, arr):
    #     if arr[6] == '':
    #         return cls(int(arr[0]), arr[1], arr[2], arr[3], None)
    #     else:
    #         return cls(int(arr[0]), arr[1], arr[2], arr[3], arr[6])
