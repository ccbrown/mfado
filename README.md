# mfado

It's like `sudo`, but for `aws` commands:

```
cbrown@mbp:~% aws s3 ls
An error occurred (AccessDenied) when calling the ListBuckets operation: Access Denied

cbrown@mbp:~% mfado aws s3 ls
MFA Code: 123456
2017-04-30 19:08:05 my-cloudtrail-bucket
2017-04-30 19:11:29 my-other-bucket
```

## Installing

Install with pip: `pip install https://github.com/ccbrown/mfado/archive/master.zip`
