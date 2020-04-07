import re


def mail_instr(strng):
    spl_line = strng.rsplit()
    mail_l = str()
    for i in spl_line:
        if re.match(".+@.+", i):
            mail_l = i
            break
    return mail_l


def clr_errstr(errstr):
    errstr = errstr.replace('\n', ' ')
    if re.match(".+ - gsmtp", errstr):
        errstr = re.sub(' 550.{1}5\.1\.1', '', errstr)
        errstr = re.sub("https://support\.google\.com/mail/\?p=NoSuchUser .+ - gsmtp",
                        "https://support.google.com/mail/?p=NoSuchUser - gsmtp", errstr)
    if re.match(".+This user doesn't have a .+ account.+", errstr):
        errstr = re.sub(' - .+', '', errstr)
        errstr = re.sub('This user doesn\'t have a .+ account', "This user doesn't have a account", errstr)
    if re.match(".+Message rejected on.+", errstr):
        errstr = re.sub(' .{4}/.{2}/.{2} .{2}:.{2}:.{2} .{3}', "", errstr)
        errstr = re.sub(' ID \(.+\) ', " ", errstr)
    return errstr


mail_log = "main.log"
# mail_log = "/var/log/exim/main.log"
date_patt = "2020-[0-9][0-9]-[0-9][0-9]"

completed = 0
mail_parsedata = dict()
err_sort_data = dict()

with open(mail_log, 'r') as f:
    for line in f:
        if re.match(date_patt, line):
                spl_line = line.rsplit()
                mail_id = spl_line[2]
                if re.match("^.{6}-.{6}-.{2}", mail_id):
                        if mail_id in mail_parsedata.keys():
                            old_lines = mail_parsedata[mail_id]["lines"]
                        else:
                            old_lines = list()
                            sendr_mail = mail_instr(line)
                            smdct = dict(send_mail=sendr_mail)
                            mail_parsedata[mail_id] = smdct
                        old_lines.append(line.rstrip())
                        mail_parsedata[mail_id]["lines"] = old_lines

for mail_id in list(mail_parsedata.keys()):
    f_line = mail_parsedata[mail_id]["lines"][0]
    spl_line = f_line.rsplit()
    if re.match(".+root@.+", f_line) or re.match(str(".+" + mail_id + " <= <>.+"), f_line) or not re.match(".+@.+", f_line):
        del mail_parsedata[mail_id]

for mail_id in mail_parsedata.keys():
    l_line = mail_parsedata[mail_id]["lines"][-1]
    res_mail = str()
    errstr = str()
    errstr_list = list()
    chck = 0
    for line in mail_parsedata[mail_id]["lines"][1::]:
        if re.match(".+" + mail_id + " .{2} ", line):
            res_mail = mail_instr(line)
            break
    mail_parsedata[mail_id]["res_mail"] = res_mail
    for line in mail_parsedata[mail_id]["lines"][1::]:
        if re.match(".+SMTP error from remote mail+", line):
            errstr= re.sub('^.+?: ', '', line)
            errstr= re.sub('^.+?: ', '', errstr)
            errstr= re.sub(res_mail, '', errstr)
            chck = 1
    if chck == 0 and re.match(".+" + mail_id + " Completed", l_line):
        mail_parsedata[mail_id]["status"] = "sended"
    elif chck == 1 and re.match(".+" + mail_id + " Completed", l_line):
        pl_line = mail_parsedata[mail_id]["lines"][-2]
        errstr = clr_errstr(errstr)
        mail_parsedata[mail_id]["errstr"] = errstr
        if re.match(str(".+" + mail_id + " => " + res_mail), pl_line):
            mail_parsedata[mail_id]["status"] = "sended"
        else:
            mail_parsedata[mail_id]["status"] = "rejected"
    elif chck != 1:
        mail_parsedata[mail_id]["errstr"] = errstr
        mail_parsedata[mail_id]["status"] = "notcompl"

sort_data = dict()
for mail_id in mail_parsedata:
    tmp_dict = mail_parsedata[mail_id]
    try:
        sort_key = tmp_dict["errstr"]
        del tmp_dict["errstr"]
        print(tmp_dict)
        # if sort_key not in sort_data:
        #     sort_data[sort_key] = tmp_dict
        # else:
        #     old_dict = sort_data[sort_key]
        #     for key in old_dict:
    except KeyError:
        pass
#

# for key in mail_parsedata.keys():
#     print(mail_parsedata[key])
