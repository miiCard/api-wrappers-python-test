api-wrapper-python-test
=======================

Test harness around the [miiCard API Python wrapper library](https://github.com/miiCard/api-wrappers-python).

This is a quick Django app intended to exercise the miiCard API Python wrapper library available on GitHub as source code and PyPI.

## Running the harness
Install the MiiCardConsumers library from PyPI:
    
    pip install MiiCardConsumers

Install Django, if you haven't already (as root if required):
    
    pip install Django

Pull down the test harness source:

    git clone git://github.com/miiCard/api-wrappers-python-test.git

Fire it up:

    cd api-wrappers-python-test
    python src/manage.py runserver 8080

Navigate to [http://localhost:8080](http://localhost:8080) - you should see the harness form.

## Usage
The test harness assumes that you have performed an OAuth exchange with the miiCard service to obtain an access token and access token secret, to complement the consumer key and consumer secret supplied to you by miiCard.

Enter the values into the four text boxes at the head of the form, then click the relevant buttons to invoke the different API functions. 

## Scope
This is intended purely for debugging and diagnostic purposes, as an aid to a developer integrating with the miiCard service - it's not intended to be a reference implementation, recommendation of good practice or anything else beyond a very basic testing platform for the API.

## Licence
Copyright (c) 2012, miiCard Limited
All rights reserved.

http://opensource.org/licenses/BSD-3-Clause

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

- Neither the name of miiCard Limited nor the names of its contributors
may be used to endorse or promote products derived from this software
without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.