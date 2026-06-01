import asyncio
import aiohttp
import ssl
from modules.base import BaseModule

class HTTPLoginModule(BaseModule):
    async def authenticate(self, username: str, password: str) -> bool:
        """
        Executes a secure asynchronous HTTP POST request to validate credentials.
        """
        # Sanitize whitespace and hidden formatting leaks from wordlists
        username = username.strip().replace('\ufeff', '')
        password = password.strip().replace('\ufeff', '')

        # 1. Dynamically build the target URL structure
        # If the port is explicitly 443 or configuration dictates secure flags, apply https
        if self.port == 443 or self.config.get('use_ssl', True):
            url = f"https://{self.target}:{self.port}{self.config.get('uri', '/login')}"
        else:
            url = f"http://{self.target}:{self.port}{self.config.get('uri', '/login')}"

        # 2. Extract dynamic parameter mappings passed from main.py's interactive prompts
        user_param = self.config.get('user_param', 'username')
        pass_param = self.config.get('pass_param', 'password')
        error_signature = self.config.get('error_signature', 'Invalid credentials')

        # Construct form payload data
        payload = {
            user_param: username,
            pass_param: password
        }

        # 3. Define headers to match standard browser properties
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TitanBruteEngine/4.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Establish connection timeouts to prevent worker starvation
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        try:
            # Create a standard SSL context tracking certificates
            ssl_context = ssl.create_default_context()
            
            # Alternative: If testing against internal laboratory targets using self-signed certs,
            # uncomment the following lines to bypass validation warnings:
            # ssl_context.check_hostname = False
            # ssl_context.verify_mode = ssl.CERT_NONE

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    url, 
                    data=payload, 
                    headers=headers, 
                    ssl=ssl_context, 
                    allow_redirects=True
                ) as response:
                    
                    # Track response text to find error identifiers
                    html_response = await response.text()

                    # Handle standard server responses
                    if response.status == 200:
                        # If the error signature is present in the HTML page, authentication failed
                        if error_signature in html_response:
                            return False
                        else:
                            # Signature missing means the error message didn't fire (Indicating success)
                            return True
                            
                    elif response.status == 429:
                        # Server-side rate limiting threshold reached
                        if self.config.get('verbose', False):
                            print(f"\n[!] Rate Limit Imposed (HTTP 429) on: {username}")
                        return False
                    else:
                        # Non-standard behavior or administrative restriction
                        return False

        except (aiohttp.ClientSSLError, ssl.SSLError) as ssl_err:
            if self.config.get('verbose', False):
                print(f"\n[!] TLS Handshake Aborted: {ssl_err}")
            return False
            
        except (aiohttp.ClientConnectorError, OSError) as net_err:
            if self.config.get('verbose', False):
                print(f"\n[!] Transport Connection Refused: {net_err}")
            return False
            
        except asyncio.TimeoutError:
            if self.config.get('verbose', False):
                print(f"\n[!] Socket Connection Timed Out.")
            return False
            
        except Exception:
            return False