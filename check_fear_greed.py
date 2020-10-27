import requests
import csv
import datetime
import math
import random
import matplotlib.pyplot as plt


def time_d(strk):
    month = strk[:3]
    if month == 'Jan':
        month = 1
    elif month == 'Feb':
        month = 2
    elif month == 'Mar':
        month = 3
    elif month == 'Apr':
        month = 4
    elif month == 'May':
        month = 5
    elif month == 'Jun':
        month = 6
    elif month == 'Jul':
        month = 7
    elif month == 'Aug':
        month = 8
    elif month == 'Sep':
        month = 9
    elif month == 'Oct':
        month = 10
    elif month == 'Nov':
        month = 11
    elif month == 'Dec':
        month = 12
    dt = datetime.date(int(strk[8:]), month, int(strk[4:6]))
    t = datetime.time(hour=3)
    dt = datetime.datetime.combine(dt, t)
    dt = datetime.datetime.fromisoformat(str(dt)).timestamp()
    return str(int(dt))


def random_generator(old_list):
    deltas = []
    for i in range(len(old_list) - 1):
        delta = math.fabs(old_list[i + 1] - old_list[i])
        deltas.append(delta)
    first_point = 0
    sign = random.choice([-1, 1])
    new_list = [first_point + sign * deltas[random.randint(0, len(deltas) - 1)]]
    min_count = float('inf')
    max_count = float('-inf')
    sum_count = new_list[0]
    for i in range(1, len(deltas)):
        sign = random.choice([-1, 1])
        new_count = new_list[i - 1] + sign * deltas[random.randint(0, len(deltas) - 1)]
        new_list.append(new_count)
        sum_count += new_count
        if new_count < min_count:
            min_count = new_count
        if new_count > max_count:
            max_count = new_count
    avg_line = sum_count / len(new_list)
    return new_list, avg_line, min_count, max_count


def get_list_whith_low_limit(old_list, low_limit):
    seq = random_generator(old_list)
    new_list = seq[0]
    avg_line = seq[1]
    min_count = seq[2]
    max_count = seq[3]
    new_list_low = []
    if min_count < low_limit:
        delta = low_limit - min_count
        for i in new_list:
            new_list_low.append(i + delta)
        new_avg_line = avg_line + delta
        max_count = max_count + delta
    else:
        delta = min_count - low_limit
        for i in new_list:
            new_list_low.append(i - delta)
        new_avg_line = avg_line - delta
        max_count = max_count - delta
    return new_list_low, new_avg_line, max_count


def extrems(list_seq, max_count, min_count, avg_line, k):
    over_line = max_count - avg_line
    under_line = avg_line - min_count
    extr = 0
    sign = None
    for i in list_seq:
        if i > avg_line and sign == True:
            continue
        elif i > avg_line and (sign == False or sign == None):
            if i - avg_line > k / 100 * over_line:
                extr += 1
                sign = True
        if i < avg_line and sign == False:
            continue
        elif i < avg_line and (sign == True or sign == None):
            if avg_line - i > k / 100 * under_line:
                extr += 1
                sign = False
    return extr


def filter_extr_avg_line(new_seq, hist_seq, hist_avg, hist_max, hist_min, new_avg, new_max, new_min, avg_line_dev=5,
                         extr_old=60,
                         extr_new=60, extr_limit_up=0, extr_limit_down=0, symmetry=True):
    new_delta = new_max - new_min
    avg_line_dev = avg_line_dev / 100
    dev = new_delta * avg_line_dev
    l = (hist_avg - hist_min) / (hist_max - hist_min)
    new_down_line = new_delta * l + new_min
    if symmetry:
        new_up_line = new_max - new_delta * l
        uu = new_up_line + dev
        ud = new_up_line - dev
        du = new_down_line + dev
        dd = new_down_line - dev
        if ud > new_avg > dd or uu > new_avg > du:
            old_extr = extrems(hist_seq, hist_max, hist_min, hist_avg, extr_old)
            new_extr = extrems(new_seq, new_max, new_min, new_avg, extr_new)
            if old_extr - extr_limit_down <= new_extr <= old_extr + extr_limit_up:
                return new_extr
            else:
                return None
        else:
            return None
    elif not symmetry:
        du = new_down_line + dev
        dd = new_down_line - dev
        if du > new_avg > dd:
            old_extr = extrems(hist_seq, hist_max, hist_min, hist_avg, extr_old)
            new_extr = extrems(new_seq, new_max, new_min, new_avg, extr_new)
            if old_extr - extr_limit_down <= new_extr <= old_extr + extr_limit_up:
                return new_extr
            else:
                return None
        else:
            return None


def check_fear_greed(hist_fear_greed, hist_min_fear, hist_max_fear, btc_price_list):
    our_money = 100
    our_btc = 0
    buy_line = hist_min_fear
    sale_line = 49
    buy_line_max = 0
    sale_line_max = 0
    max_money = 0
    positive_result = 0
    negative_result = 0
    buy_seq = []
    sale_seq = []
    sum_positive_result = 0
    while buy_line < 50:
        sale_line += 1
        for i in range(len(hist_fear_greed)):
            if hist_fear_greed[i] <= buy_line and our_btc == 0:
                our_btc = our_money / btc_price_list[i] - (our_money / btc_price_list[i] * 0.001)
                our_money = 0
                # if buy_line == 12 and sale_line == 65:
                #     print('buy:', btc_price_list[i], hist_fear_greed[i])
            elif hist_fear_greed[i] >= sale_line and our_money == 0:
                our_money = our_btc * btc_price_list[i] - (our_btc * btc_price_list[i] * 0.001)
                our_btc = 0
                # if buy_line == 12 and sale_line == 65:
                #     print('sale:', btc_price_list[i], hist_fear_greed[i])
        if our_btc:
            itog_money = our_btc * 10621.66
        else:
            itog_money = our_money
        if itog_money > 100:
            positive_result += 1
            # print("расчет идет на: buy =", buy_line, ", sale =", sale_line,'itog money=', itog_money)
            buy_seq.append(buy_line)
            sale_seq.append(sale_line)
            sum_positive_result += itog_money
        elif itog_money <= 100:
            negative_result += 1
        if max_money < itog_money:
            buy_line_max = buy_line
            sale_line_max = sale_line
            max_money = itog_money
        our_money = 100
        our_btc = 0
        if sale_line == hist_max_fear:
            buy_line += 1
            sale_line = 49
    percent_pos_issue = positive_result / (positive_result + negative_result) * 100
    if positive_result:
        avg_positive_result = sum_positive_result / positive_result
    else:
        avg_positive_result = 0
    return buy_line_max, sale_line_max, max_money, percent_pos_issue, buy_seq, sale_seq, avg_positive_result


hist_fear_greed = []
ind = requests.get('https://api.alternative.me/fng/', params={'limit': '0'})
for i in ind.json()['data']:
    if int(i['timestamp']) > 1601942400 + 86400 * 3:
        continue
    else:
        hist_fear_greed.insert(0, int(i['value']))

hist_btc = []
with open('D:\\simulator\\1.csv') as f:
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        time_st = time_d(row[0])
        cost = row[1].replace('К', '')
        cost = cost.replace(',', '.')
        hist_btc.insert(0, float(cost))

hist_min_fear = min(hist_fear_greed)
hist_max_fear = max(hist_fear_greed)
hist_fear_greed_avg = sum(hist_fear_greed) / len(hist_fear_greed)
hist_btc_min = min(hist_btc)
hist_btc_max = max(hist_btc)
hist_btc_avg = sum(hist_btc) / len(hist_btc)


y_price_hist = hist_btc
x_days = [i for i in range(1, len(y_price_hist) + 1)]
fig = plt.figure()

axes1 = fig.add_axes([0.15, 0.55, 0.8, 0.35])
axes2 = fig.add_axes([0.15, 0.1, 0.8, 0.35])

axes1.hlines(hist_btc_avg, 0, len(x_days), colors='r')
axes1.grid()
axes1.plot(x_days, y_price_hist, 'b')
axes1.set_xlabel('days                                                                           ')
axes1.set_ylabel('price')
axes1.set_title('BTC price')

axes2.hlines(hist_fear_greed_avg, 0, len(x_days), colors='r')
axes2.grid()
axes2.plot(x_days, hist_fear_greed, 'g')
axes2.set_xlabel('days')
axes2.set_ylabel('index')
axes2.set_title('Fear-Greed index')
plt.show()

check = check_fear_greed(hist_fear_greed, hist_min_fear, hist_max_fear, hist_btc)
real_buy_line_max = check[0]
real_sale_line_max = check[1]
real_max_money = check[2]
real_pos_res = check[3]
real_pos_money = check[6]

buy_pos_seq = check[4]
sale_pos_seq = check[5]

print('OUR REALITY:  buy line=', round(real_buy_line_max, 2), ';sale line=', round(real_sale_line_max, 2),
      ';max money=', round(real_max_money, 2), ';POS RES%=', round(real_pos_res, 2),
      ';pos money$=', round(real_pos_money, 2))

plt.grid()
plt.plot(buy_pos_seq, sale_pos_seq)
plt.xlim([0, 50])
plt.ylim([50, 100])
plt.xlabel('buy line')
plt.ylabel('sale line')
plt.title('POSITIVE RESULT ZONE')
plt.show()

new_min = 3300

avg_buy_line_max = 0
avg_sale_line_max = 0
avg_max_money = 0
avg_pos_res = 0
avg_pos_money = 0
z = 0
iterations = 100
while z <= iterations:
    f = get_list_whith_low_limit(hist_btc, new_min)
    new_list = f[0]
    new_avg = f[1]
    new_max = f[2]
    if 12000 < new_max < 14000:
        a = filter_extr_avg_line(new_list, hist_btc, hist_btc_avg, hist_btc_max, hist_btc_min, new_avg, new_max,
                                 new_min, avg_line_dev=5,
                                 extr_old=60,
                                 extr_new=60, extr_limit_up=0, extr_limit_down=0, symmetry=True)
        if a:
            z += 1
            check = check_fear_greed(hist_fear_greed, hist_min_fear, hist_max_fear, new_list)
            avg_buy_line_max += check[0]
            avg_sale_line_max += check[1]
            avg_max_money += check[2]
            avg_pos_res += check[3]
            avg_pos_money += check[6]
            print('Reality №:', z, 'of', iterations, ';buy line=', round(check[0], 2), ';sale line=',
                  round(check[1], 2),
                  ';max money=', round(check[2], 2), ';POS RES%=', round(check[3], 2),
                  ';pos money$=', round(check[6], 2))

print('ALTER. AVG REALITY:  avg buy line=', round(avg_buy_line_max / iterations, 2), ';avg sale line=',
      round(avg_sale_line_max / iterations, 2),
      ';avg max money=', round(avg_max_money / iterations, 2), ';AVG POS RES%=', round(avg_pos_res / iterations, 2),
      ';avg pos money$=', round(avg_pos_money / iterations, 2))

# print('max money=', check[2], ';avg pos rez=', avg_pos_result, ';all pos result%=', check[3], ';avg pos $=', check[6])


# x_price_new = [i for i in new_list]
# y_price = [i for i in range(1, len(x_price_new) + 1)]
# fig, ax = plt.subplots()
# ax.hlines(new_avg, 0, max(y_price), colors='r')
# plt.plot(y_price, x_price_new)
#
# plt.show()

# x2_price_hist_fear = hist_fear_greed

# x_price_new = [i for i in count]
# y_price = [i for i in range(1, len(x_price_new) + 1)]
# fig, ax = plt.subplots()
# # ax.hlines(new_avg, 0, max(y_price), colors='r')
# plt.plot(y_price, x_price_new)
# plt.show()
