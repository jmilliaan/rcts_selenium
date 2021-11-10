<h1>Real-Time Competition Tracking System</h1>
Program Kerja Divisi Eksternal BEM CIT 2021/2022 <br>
Helps in getting events from several instagram accounts. Events or competition scraped from these accounts will help university students find competitions to join. <br>
<h2>Install</h2>
1. Chrome browser must be installed <br>
2. Download <a href="https://sites.google.com/a/chromium.org/chromedriver/" rel="nofollow">chromedriver</a> and put it into  the program directory <br>
3. Install requirements: <code>pip install -r requirements.txt </code> <br>

<h2>Input</h2>
  <h3>Username List</h3>
    Input type: <code>string</code><br>
    The input for this program is an .xlsx file containing instagram usernames. <br>
    The input file in this repository is <code>informasilomba.xlsx</code> and contains 8 instagram accounts. The first cell must be       the string "username". <br>
  <h3>Number of Posts</h3>
    Determine the number of posts to take from each instagram user account. 
  <h3>Timing Coefficient</h3>
    Input type: <code>int</code><br>
    Internet speeds may vary. To avoid errors due to the page not loading, increase the timing coefficient. Default timing        coefficient is 1. <br>
    The timing coefficient multiplies all waiting time. Increasing the timing coefficient to 2 will make the program twice slower,  and so on. <br>
   <h3>Filter Keywords</h3>
      Input type: <code>boolean</code><br>
      By default, the program will run the <code>.filter_lomba()</code> method to only add posts about competitions. Setting this to <code>False</code> will not run said method. 
<h2>Run Program</h2>
Type in command prompt/terminal:<br>

```
python main.py filename number_of_posts timing_coefficient filter_keywords
```
<br> **Example:**<br>


```
python main.py informasilomba.xlsx 3 1.2 True
```

Takes 3 posts from each username in <code>informasilomba.xlsx</code> and multiplies all delays by 1.2. The output will then be filtered. 
<h2>Output</h2>
This program outputs a file named <code>rcts_date.xlsx</code><br>
Example: <code>rcts_10-03-21.xlsx</code><br>
