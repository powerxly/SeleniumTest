# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import time

from selenium.webdriver.remote.errorhandler import ErrorCode
from selenium.webdriver.remote.errorhandler import ErrorHandler

from selenium.common.exceptions import (ElementNotInteractableException,
                                        ElementNotSelectableException,
                                        ElementNotVisibleException,
                                        ErrorInResponseException,
                                        InvalidElementStateException,
                                        InvalidSelectorException,
                                        ImeNotAvailableException,
                                        ImeActivationFailedException,
                                        MoveTargetOutOfBoundsException,
                                        NoSuchElementException,
                                        NoSuchFrameException,
                                        NoSuchWindowException,
                                        NoAlertPresentException,
                                        StaleElementReferenceException,
                                        TimeoutException,
                                        UnexpectedAlertPresentException,
                                        WebDriverException)

try:
    basestring
except NameError:  # Python 3.x
    basestring = str

__default_encoding__="gbk"

class MyErrorHandler(ErrorHandler):
    """
    Handles errors returned by the WebDriver server.
    """
    screen_shot=False
    last_status=''
    def __init__(self,driver,screen_shot=False,site=''):
        self.driver = driver
        self.screen_shot = screen_shot
        self.site = site
    def check_response(self, response):
        """
        Checks that a JSON response from the WebDriver does not have an error.

        :Args:
         - response - The JSON response from the WebDriver server as a dictionary
           object.

        :Raises: If the response contains an error message.
        """
        status = response.get('status', None)
        if status is None or status == ErrorCode.SUCCESS:
            return
        #print(response)
        value = None
        message = response.get("message", "")
        screen = response.get("screen", "")
        stacktrace = None
        if isinstance(status, int):
            value_json = response.get('value', None)
            if value_json and isinstance(value_json, basestring):
                import json
                try:
                    value = json.loads(value_json)
                    if len(value.keys()) == 1:
                        value = value['value']
                    status = value.get('error', None)
                    if status is None:
                        status = value["status"]
                        message = value["value"]
                        if not isinstance(message, basestring):
                            value = message
                            message = message.get('message')
                    else:
                        message = value.get('message', None)
                except ValueError:
                    pass

        if (self.screen_shot):
            if self.last_status!=status:
                print('response status:------%s' % status)
                #capture a screenshot of the screen when exception first occurs. In some condition, exception should be ignored when in "tring or waiting time". that should be completed in future.
                if isinstance(status, int):
                    txt_status = 'status_%d' % status
                else:
                    txt_status = status
                now = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime(time.time()))
                filename=txt_status.replace(' ','_')
                site=''
                if self.site!='':
                    site = self.site +'-'
                filename = "./error_picture/"+site+now+'-'+filename+'.png'
                print('filename:%s' % filename)
                try:
                    self.__save_screenshot(filename)
                except:
                    print('error in save screenshot while error occurs')
                    pass
                self.last_status = status

        exception_class = ErrorInResponseException
        if status in ErrorCode.NO_SUCH_ELEMENT:
            exception_class = NoSuchElementException
        elif status in ErrorCode.NO_SUCH_FRAME:
            exception_class = NoSuchFrameException
        elif status in ErrorCode.NO_SUCH_WINDOW:
            exception_class = NoSuchWindowException
        elif status in ErrorCode.STALE_ELEMENT_REFERENCE:
            exception_class = StaleElementReferenceException
        elif status in ErrorCode.ELEMENT_NOT_VISIBLE:
            exception_class = ElementNotVisibleException
        elif status in ErrorCode.INVALID_ELEMENT_STATE:
            exception_class = InvalidElementStateException
        elif status in ErrorCode.INVALID_SELECTOR \
                or status in ErrorCode.INVALID_XPATH_SELECTOR \
                or status in ErrorCode.INVALID_XPATH_SELECTOR_RETURN_TYPER:
            exception_class = InvalidSelectorException
        elif status in ErrorCode.ELEMENT_IS_NOT_SELECTABLE:
            exception_class = ElementNotSelectableException
        elif status in ErrorCode.ELEMENT_NOT_INTERACTABLE:
            exception_class = ElementNotInteractableException
        elif status in ErrorCode.INVALID_COOKIE_DOMAIN:
            exception_class = WebDriverException
        elif status in ErrorCode.UNABLE_TO_SET_COOKIE:
            exception_class = WebDriverException
        elif status in ErrorCode.TIMEOUT:
            exception_class = TimeoutException
        elif status in ErrorCode.SCRIPT_TIMEOUT:
            exception_class = TimeoutException
        elif status in ErrorCode.UNKNOWN_ERROR:
            exception_class = WebDriverException
        elif status in ErrorCode.UNEXPECTED_ALERT_OPEN:
            exception_class = UnexpectedAlertPresentException
        elif status in ErrorCode.NO_ALERT_OPEN:
            exception_class = NoAlertPresentException
        elif status in ErrorCode.IME_NOT_AVAILABLE:
            exception_class = ImeNotAvailableException
        elif status in ErrorCode.IME_ENGINE_ACTIVATION_FAILED:
            exception_class = ImeActivationFailedException
        elif status in ErrorCode.MOVE_TARGET_OUT_OF_BOUNDS:
            exception_class = MoveTargetOutOfBoundsException
        else:
            exception_class = WebDriverException
        if value == '' or value is None:
            value = response['value']
        if isinstance(value, basestring):
            if exception_class == ErrorInResponseException:
                raise exception_class(response, value)
            raise exception_class(value)
        if message == "" and 'message' in value:
            message = value['message']

        screen = None
        if 'screen' in value:
            screen = value['screen']

        stacktrace = None
        if 'stackTrace' in value and value['stackTrace']:
            stacktrace = []
            try:
                for frame in value['stackTrace']:
                    line = self._value_or_default(frame, 'lineNumber', '')
                    file = self._value_or_default(frame, 'fileName', '<anonymous>')
                    if line:
                        file = "%s:%s" % (file, line)
                    meth = self._value_or_default(frame, 'methodName', '<anonymous>')
                    if 'className' in frame:
                        meth = "%s.%s" % (frame['className'], meth)
                    msg = "    at %s (%s)"
                    msg = msg % (meth, file)
                    stacktrace.append(msg)
            except TypeError:
                pass
        if exception_class == ErrorInResponseException:
            raise exception_class(response, message)
        elif exception_class == UnexpectedAlertPresentException and 'alert' in value:
            raise exception_class(message, screen, stacktrace, value['alert'].get('text'))
        raise exception_class(message, screen, stacktrace)
    #capture a screenshot 
    def __save_screenshot(self, filePath=""):
        if filePath!="":
            filePath=filePath.decode(__default_encoding__)
            self.driver.save_screenshot(filePath)
