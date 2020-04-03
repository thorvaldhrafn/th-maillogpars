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
mail_resdata = dict()
mail_faildata = dict()
mail_notcompl = dict()
err_sort_data = dict()

with open(mail_log, 'r') as f:
    for line in f:
        if re.match(date_patt, line):
                spl_line = line.rsplit()
                mail_id = spl_line[2]
                if re.match("^.{6}-.{6}-.{2}", mail_id):
                        if mail_id in mail_parsedata.keys():
                            old_lines = mail_parsedata[mail_id]
                        else:
                            old_lines = list()
                        old_lines.append(line.rstrip())
                        mail_parsedata[mail_id] = old_lines

mail_idlist = list(mail_parsedata.keys())

for mail_id in mail_idlist:
    f_line = mail_parsedata[mail_id][0]
    spl_line = f_line.rsplit()
    if re.match(".+root@.+", f_line) or re.match(str(".+" + mail_id + " <= <>.+"), f_line) or not re.match(".+@.+", f_line):
        del mail_parsedata[mail_id]

for mail_id in mail_parsedata.keys():
    f_line = mail_parsedata[mail_id][0]
    l_line = mail_parsedata[mail_id][-1]
    sendr_mail = mail_instr(f_line)
    res_mail = str()
    errstr = str()
    errstr_list = list()
    chck = 0
    for line in mail_parsedata[mail_id][1::]:
        if re.match(".+" + mail_id + " .{2} ", line):
            res_mail = mail_instr(line)
            break
    for line in mail_parsedata[mail_id][1::]:
        if re.match(".+SMTP error from remote mail+", line):
            errstr= re.sub('^.+?: ', '', line)
            errstr= re.sub('^.+?: ', '', errstr)
            errstr= re.sub(res_mail, '', errstr)
            chck = 1
    if chck == 0 and re.match(".+" + mail_id + " Completed", l_line):
        mail_resdata[mail_id] = dict(res_mail=res_mail)
    elif chck == 1 and re.match(".+" + mail_id + " Completed", l_line):
        pl_line = mail_parsedata[mail_id][-2]
        if re.match(str(".+" + mail_id + " => " + res_mail), pl_line):
            mail_resdata[mail_id] = dict(res_mail=res_mail)
        else:
            errstr = clr_errstr(errstr)
            mail_faildata[mail_id] = dict(res_mail=res_mail, errstr=errstr)
            if errstr in err_sort_data.keys():
                old_mlist = err_sort_data[errstr]["emails"]
                old_mlist.append(res_mail)
            else:
                err_sort_data[errstr] = dict(emails=[res_mail])

    elif chck != 1:
        mail_notcompl[mail_id] = dict(res_mail=res_mail, errstr=mail_parsedata[mail_id][-1])


# for mail_id in mail_faildata.keys():
#     print(mail_faildata[mail_id]["res_mail"])
#     print(mail_faildata[mail_id]["errstr"])
print(len(mail_resdata))
print(len(mail_faildata))
print(len(mail_notcompl))

# for err in err_sort_data:
#     print(err)
#     # print(err_sort_data[err])

for key in mail_notcompl.keys():
    print(mail_notcompl[key])

# for line in mail_parsedata["1jIrEn-0007Jn-7s"]:
#     print(line)
