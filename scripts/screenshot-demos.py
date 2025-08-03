#!/usr/bin/env python3
"""
ScummVM Demo Testing Script

This script uses a headless browser to:
1. Visit https://scummvm-test.kuendig.io/games.html
2. Extract all links to ScummVM demos 
3. Test each demo by loading it and taking a screenshot after 10 seconds
4. Save screenshots with names based on the game path
"""

import asyncio
import re
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote
from playwright.async_api import async_playwright
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScummVMDemoTester:
    def __init__(self, base_url="https://scummvm-test.kuendig.io", 
                 screenshot_dir="screenshots", timeout=10000, max_concurrent=10):
        self.base_url = base_url
        self.games_url = f"{base_url}/games.html"
        self.scummvm_url = f"{base_url}/scummvm.html"
        self.screenshot_dir = Path(screenshot_dir)
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.screenshot_dir.mkdir(exist_ok=True)
        
    async def extract_demo_links(self, page):
        """Extract all ScummVM demo links from games.html"""
        logger.info(f"Visiting {self.games_url}")
        await page.goto(self.games_url, wait_until="networkidle")
        
        # Find all links that point to scummvm.html with path parameters
        links = await page.evaluate("""
            Array.from(document.querySelectorAll('a[href*="scummvm.html"]'))
                .map(link => link.href)
                .filter(href => href.includes('--path='))
        """)
        
        logger.info(f"Found {len(links)} demo links")
        return links
    
    def extract_game_name_from_url(self, url):
        """Extract game name from ScummVM URL for screenshot naming"""
        try:
            # Parse the URL fragment after #
            parsed = urlparse(url)
            fragment = parsed.fragment
            
            if not fragment:
                return "unknown"
            
            # Look for --path= parameter
            path_match = re.search(r'--path=([^%\s]+)', fragment)
            if path_match:
                path = unquote(path_match.group(1))
                # Extract the last part of the path
                game_name = Path(path).name
                # Clean up the name for filesystem
                game_name = re.sub(r'[^\w\-_.]', '_', game_name)
                return game_name
            
            return "unknown"
        except Exception as e:
            logger.warning(f"Failed to extract game name from {url}: {e}")
            return "unknown"
    
    async def test_demo_parallel(self, browser, semaphore, demo_url, game_name, demo_index, total_count):
        """Test a single demo by loading it and taking a screenshot (parallel version)"""
        async with semaphore:  # Limit concurrent demos
            # Create a fresh page for each demo to avoid state interference
            page = await browser.new_page()
            
            try:
                # Set viewport size for consistent screenshots
                await page.set_viewport_size({"width": 1440, "height": 1080})
                
                logger.info(f"Testing demo {demo_index}/{total_count}: {game_name} ({demo_url})")
                
                # Set up console message monitoring
                console_messages = []
                def handle_console(msg):
                    console_messages.append(msg.text)
                    logger.debug(f"Console [{game_name}]: {msg.text}")
                
                page.on("console", handle_console)
                
                # Navigate to the demo
                await page.goto(demo_url, wait_until="networkidle", timeout=30000)
                
                # Wait for the specific console message indicating the game has been selected
                logger.info(f"Waiting for game selection message for {game_name}...")
                target_message_found = False
                max_wait_time = 30  # Maximum time to wait for the message (seconds)
                start_time = asyncio.get_event_loop().time()
                
                while not target_message_found and (asyncio.get_event_loop().time() - start_time) < max_wait_time:
                    # Check if we've seen the target message
                    for message in console_messages:
                        if "User picked target" in message and "engine ID" in message and "game ID" in message:
                            logger.info(f"Found target selection message for {game_name}: {message}")
                            target_message_found = True
                            break
                    
                    if not target_message_found:
                        await asyncio.sleep(0.5)  # Check every 500ms
                
                if not target_message_found:
                    logger.warning(f"Timeout waiting for game selection message for {game_name}")
                    # Still proceed with screenshot after timeout
                
                # Wait for 10 seconds after the game selection message
                logger.info(f"Waiting 20 seconds for {game_name} to load...")
                await asyncio.sleep(20)
                
                # Take screenshot
                screenshot_path = self.screenshot_dir / f"{game_name}.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)
                
                logger.info(f"Screenshot saved: {screenshot_path}")
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to test demo {game_name}: {e}")
                return False
            finally:
                # Always close the page to clean up
                await page.close()

    async def test_demo(self, page, demo_url, game_name):
        """Test a single demo by loading it and taking a screenshot"""
        try:
            logger.info(f"Testing demo: {game_name} ({demo_url})")
            
            # Navigate to the demo
            await page.goto(demo_url, wait_until="networkidle", timeout=30000)
            
            # Wait for 10 seconds to let the game load
            logger.info(f"Waiting 10 seconds for {game_name} to load...")
            await asyncio.sleep(10)
            
            # Take screenshot
            screenshot_path = self.screenshot_dir / f"{game_name}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            logger.info(f"Screenshot saved: {screenshot_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to test demo {game_name}: {e}")
            return False
    
    async def run_tests(self):
        """Run all demo tests in parallel"""
        async with async_playwright() as p:
            # Launch browser in headless mode
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            try:
                # Create a page just for extracting demo links
                links_page = await browser.new_page()
                await links_page.set_viewport_size({"width": 1440, "height": 1080})
                
                # Extract demo links
                demo_links = await self.extract_demo_links(links_page)
                
                # Close the links page as we don't need it anymore
                await links_page.close()
                
                if not demo_links:
                    logger.warning("No demo links found!")
                    return
                
                # Filter out demos that already have screenshots
                demos_to_test = []
                skipped_count = 0
                total_count = len(demo_links)
                
                for i, demo_url in enumerate(demo_links, 1):
                    game_name = self.extract_game_name_from_url(demo_url)
                    screenshot_path = self.screenshot_dir / f"{game_name}.png"
                    
                    # Skip if screenshot already exists
                    if screenshot_path.exists():
                        logger.info(f"Skipping demo {i}/{total_count}: {game_name} (screenshot already exists)")
                        skipped_count += 1
                        continue
                    
                    demos_to_test.append((demo_url, game_name, i))
                
                if not demos_to_test:
                    logger.info(f"All {total_count} demos already have screenshots!")
                    return
                
                logger.info(f"Testing {len(demos_to_test)} demos in parallel (max {self.max_concurrent} concurrent)")
                
                # Create semaphore to limit concurrent demos
                semaphore = asyncio.Semaphore(self.max_concurrent)
                
                # Create tasks for parallel execution
                tasks = [
                    self.test_demo_parallel(browser, semaphore, demo_url, game_name, demo_index, total_count)
                    for demo_url, game_name, demo_index in demos_to_test
                ]
                
                # Run all tasks and collect results
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count successful tests
                success_count = sum(1 for result in results if result is True)
                error_count = sum(1 for result in results if isinstance(result, Exception))
                
                logger.info(f"Parallel testing completed: {success_count}/{len(demos_to_test)} successful, {skipped_count} skipped, {error_count} errors")
                
            finally:
                await browser.close()

async def main():
    """Main entry point"""
    tester = ScummVMDemoTester()
    await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main())