# Used
Here are dashboarding software that have been used before, thus reviewing from experience. Arranged in order of preference (highest to lowest).
## Dash
- By plotly, available in both Python and R
- Hosted with flask (no configs required)
- In Python you can insert matplotlib plots
- Compared to others, this gives you very little to start with
- Documentation good
- No grids, ugly default styling, takes time to make it look good
- Implement onHover or onClick and make calculations (others can only do this via DB queries)
- Custom dropdowns, selectable variables, whatever
- Can reuse computation/results, not really possible with others
- Grab data however you want, DBMS, csv, requests, etc.
- Requirements: Some HTML knowledge. CSS if you want it to look good
    - Python, matplotlib
    - Also means you'll be aligning divs X)
- Tracebacks when something fails
- [Documentation](https://dash.plotly.com/): One of the best here
- Looks 2/5
- 20.6k stars on GitHub, you probably already know how to use matplotlib (discussions are also fairly active thanks to matplotlib)
- https://dash.plotly.com/

## Grafana
- Limited to already developed charts
- GUI development (some help with SQL queries)
- Requirements: Grafana syntax, SQL queries
- Relies on DB queries
- Heatmaps
- Limited variable support (no `if` but workarounds using SQL `union` possible)
- Chart arrangement uses grids
- Dark mode
- Has third party plugin support (documentation for these might be worse)
- Little help when something fails
- [Documentation](https://grafana.com/docs/): Main page of docs is a chatbot :). Other docs pages are fairly basic, only describes what they do.
- Looks 4.5/5
- 60.6k stars on GitHub, discussions very rarely answered on their forums
- https://grafana.com/

## Ratings/personal thoughts:
### Writer 1
- Dash: Takes a long time to configure and look good, but if you want the most interactivity or quirky plots this is the only way to go
- Grafana: Quick to set up, documentation on setting up variables are a mess (virtually none)
    - variables are passed through parameters in url
    - conditional statements achievable through `where` and `union all`
### Writer 2
- Please add what you've used here :) Also add to above/below sections.


# Unused
Here are dashboarding software that have not been used, judging based off searches/documentation. Arranged in order of preference (highest to lowest).

## Metabase
- Limited to already developed charts
- GUI development (SQL editor seems pretty good)
- Relies on DB queries
- Heatmaps
- Like grafana but with multiple plots on same graph
- Variables similar to grafana but easier to add (better documentation)
- Dropdowns also look better than grafana
- [Documentation](https://www.metabase.com/docs/latest/) Detailed for many of the features, limited in dashboard/plotting
- Looks 5/5
- 36.7k stars on GitHub, discussions somewhat active
- Seems good but many bloated features for demo
- This looks to have the best interactivity

## Redash
- Limited to already developed charts (includes maps, sankey, sunburst)
- GUI development (some help with SQL queries)
- Can integrate python scripts into charts
- [Documentation](https://redash.io/help/): Limited pages but very detailed (little help on start)
- Discussion fairly active
- Relies on DB queries
- Looks 4/5
- 25k stars on GitHub, discussions not very active
- (Honestly this looks like grafana with extra sauce, doesn't look like they have dark mode though)

## Seal Report
- Limited to already developed charts
- [Windows only (requires additional drivers on linux)](https://sealreport.org/#lineOverview_2)
- GUI development (some help with SQL queries)
- Relies on DB queries
- Looks like its more for enterprise level deployment
    - Able to check windows user running DB to check access
- Has `if`, `while`, supports variables
- [Documentation](https://sealreport.org/): Questionable/simplistic
- Looks: 3.5/5
- 1.4k stars on GitHub, also has a forum (not very active)
- https://sealreport.org/

## Dashboard Builder
- Limited to already developed charts
- GUI development (some help with SQL queries)
- Relies on DB queries, has support for excel/Google Sheets, json
- 3D plots
- Turn charts into php code (has innate support for rendering as well)
- Free transform on charts (not limited on size/location of charts)
- [Documentation](https://dashboardbuilder.net/apply-filter-to-a-chart): Very basic picture based documentation (noob friendly)
- Looks 3.5/5
- 20 stars on GitHub
- https://dashboardbuilder.net/

## Countly
- LIKELY UNSUITABLE
- Heavily geared towards enterprise solutions (docs reflect this)
- [Documentation](https://support.count.ly/hc/en-us) Extremely detailed
- 5.5k stars on GitHub

## Dashy
- Extremely limited (to already developed widgets)
- Dashboard development revolves around configs (json/yaml)
- Can add own widgets (vue)
- Requires docker
- [Documentation](https://dashy.to/docs/): Good
- Looks: 5/5
- 15.6k stars on GitHub
- Discussions kinda active (nothing on stackoverflow)
- https://dashy.to/
## Keen
- Looks 4/5
- JS based, but I think has GUI development
    - I think grabbing data requires get/post requests
- 11k stars on GitHub
- I'd skip
