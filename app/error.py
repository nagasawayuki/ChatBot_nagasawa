class LongTextException(Exception):
  def __init__(self, length):
    self.text_length=length

class NoMeaningException(Exception):
    pass
   
class GeminiException(Exception):
    pass

class MessengerAPIError(Exception):
   pass

class HTTPRequestError(Exception):
   pass