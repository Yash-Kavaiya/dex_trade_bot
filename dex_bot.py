from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from web3 import Web3
import asyncio
import logging
import json
import aiohttp
from decimal import Decimal

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class DEXBot:
    def __init__(self, telegram_token: str, web3_provider: str):
        self.telegram_token = telegram_token
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        
        # Standard DEX contract ABI (simplified example)
        self.dex_abi = json.loads('''[
            {"type": "function", "name": "getReserves", 
             "inputs": [], 
             "outputs": [{"type": "uint112"}, {"type": "uint112"}]},
            {"type": "function", "name": "token0", 
             "inputs": [], 
             "outputs": [{"type": "address"}]},
            {"type": "function", "name": "token1", 
             "inputs": [], 
             "outputs": [{"type": "address"}]}
        ]''')

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /start command"""
        keyboard = [
            [InlineKeyboardButton("📊 Token Analysis", callback_data='analyze')],
            [InlineKeyboardButton("💹 Price Alerts", callback_data='alerts')],
            [InlineKeyboardButton("ℹ️ Help", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Welcome to DEX Analysis Bot!\n\n"
            "I can help you analyze tokens and track prices on decentralized exchanges.\n"
            "Select an option to get started:",
            reply_markup=reply_markup
        )

    async def analyze_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze token metrics and liquidity"""
        try:
            # Get token address from command
            token_address = context.args[0]
            if not self.w3.is_address(token_address):
                await update.message.reply_text("❌ Invalid token address provided")
                return

            # Get token contract
            token_contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(token_address),
                abi=self.dex_abi
            )

            # Fetch basic token info
            analysis_text = await self._get_token_analysis(token_contract)
            await update.message.reply_text(analysis_text)

        except Exception as e:
            logging.error(f"Error in token analysis: {str(e)}")
            await update.message.reply_text("❌ Error analyzing token. Please try again.")

    async def _get_token_analysis(self, token_contract) -> str:
        """Helper method to analyze token metrics"""
        try:
            # Get token reserves
            reserves = await token_contract.functions.getReserves().call()
            
            # Calculate basic metrics
            liquidity = Decimal(reserves[0]) / Decimal(10**18)
            
            analysis = (
                f"📊 Token Analysis\n\n"
                f"Liquidity: {liquidity:.2f} ETH\n"
                f"24h Volume: {self._get_24h_volume(token_contract)}\n"
                f"Holders: {await self._get_holder_count(token_contract.address)}\n"
                f"Security Score: {await self._calculate_security_score(token_contract)}/100"
            )
            
            return analysis

        except Exception as e:
            logging.error(f"Error in _get_token_analysis: {str(e)}")
            raise

    async def _get_24h_volume(self, token_contract) -> Decimal:
        """Calculate 24h trading volume"""
        # Implementation would fetch and aggregate DEX trades
        # This is a placeholder returning mock data
        return Decimal('1000.00')

    async def _get_holder_count(self, token_address: str) -> int:
        """Get number of token holders"""
        # Implementation would query blockchain for unique token holders
        # This is a placeholder
        return 150

    async def _calculate_security_score(self, token_contract) -> int:
        """Calculate basic security metrics for the token"""
        score = 0
        
        try:
            # Check if contract is verified
            score += 20
            
            # Check liquidity lock
            if await self._check_liquidity_lock(token_contract):
                score += 30
            
            # Check ownership renounced
            if await self._check_ownership_renounced(token_contract):
                score += 25
            
            # Check for suspicious functions
            if not await self._check_suspicious_functions(token_contract):
                score += 25
                
        except Exception as e:
            logging.error(f"Error in security score calculation: {str(e)}")
            
        return score

    async def set_alert(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set price alert for a token"""
        try:
            token_address, price_target = context.args
            
            if not self.w3.is_address(token_address):
                await update.message.reply_text("❌ Invalid token address")
                return
                
            # Store alert in database
            await self._store_alert(
                user_id=update.effective_user.id,
                token_address=token_address,
                price_target=Decimal(price_target)
            )
            
            await update.message.reply_text(
                f"✅ Alert set! You'll be notified when the token reaches {price_target}"
            )
            
        except Exception as e:
            logging.error(f"Error setting alert: {str(e)}")
            await update.message.reply_text("❌ Error setting alert. Please try again.")

    async def _store_alert(self, user_id: int, token_address: str, price_target: Decimal):
        """Store price alert in database"""
        # Implementation would store alert in database
        pass

    def run(self):
        """Start the bot"""
        application = Application.builder().token(self.telegram_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("analyze", self.analyze_token))
        application.add_handler(CommandHandler("alert", self.set_alert))
        
        # Start the bot
        application.run_polling()

if __name__ == "__main__":
    # Initialize and run bot
    bot = DEXBot(
        telegram_token="YOUR_TELEGRAM_TOKEN",
        web3_provider="YOUR_WEB3_PROVIDER_URL"
    )
    bot.run()
