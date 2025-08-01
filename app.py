from flask import Flask, render_template, request
from pytrends.request import TrendReq

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    region_table = None
    trending = None
    selected_action = None
    if request.method == 'POST':
        selected_action = request.form.get('action')
        if selected_action == 'trending':
            region = request.form.get('trending_region', 'united_states').strip().lower()
            valid_trending_regions = ['united_states', 'japan']
            if region not in valid_trending_regions:
                error = f"Region '{region}' is not supported for trending topics. Please select United States or Japan."
            else:
                try:
                    pytrends = TrendReq(hl='en-US', tz=360)
                    trending_df = pytrends.trending_searches(pn=region)
                    trending = trending_df[0].tolist()
                except Exception as e:
                    error = f"Could not fetch trending topics: {str(e)}"
        elif selected_action == 'interest':
            keywords = request.form.get('keywords', '').strip()
            country = request.form.get('country', '').strip().upper()
            if not keywords or not country:
                error = "Please enter both keywords and a country code."
            else:
                try:
                    kw_list = [k.strip() for k in keywords.split(',') if k.strip()]
                    pytrends = TrendReq(hl='en-US', tz=360)
                    pytrends.build_payload(kw_list, timeframe='2004-01-01 2017-01-01', geo=country)
                    df = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)
                    df = df.reset_index()
                    # Only keep columns that are in kw_list (plus the region column)
                    region_col = df.columns[0]
                    keep_cols = [region_col] + [col for col in df.columns if col in kw_list]
                    df = df[keep_cols]
                    # Only show regions with nonzero interest
                    if len(kw_list) > 0:
                        df = df[df[kw_list].sum(axis=1) > 0]
                    region_table = df
                except Exception as e:
                    error = f"Could not fetch interest by region: {str(e)}"
    return render_template('index.html', region_table=region_table, trending=trending, error=error, selected_action=selected_action)

if __name__ == '__main__':
    app.run(debug=True)