import urllib.request, json


def main():
    sum = claim_data("DAI", "0xb374387a340e6aA7d78385C4a4aaC6b425A685B0") + claim_data("USDC", "0x4140F350c1B67184fE3AaEa314d8C967F99EE8Cc") + claim_data("WETH", "0xFc84A04478Ffe0B48e46048f4E933A51F4016289")
    print(f'total sum {sum} rooks')

def claim_data(token: str, address: str):
    with urllib.request.urlopen(f"https://indibo-lpq3.herokuapp.com/reward_of_liquidity_provider/{address}") as url:
        data = json.loads(url.read().decode())
        amount = int(data["earnings_to_date"], 16)/1e18
        print(f'StrategyRook{token} has accrued {amount} total rook')
        return amount
