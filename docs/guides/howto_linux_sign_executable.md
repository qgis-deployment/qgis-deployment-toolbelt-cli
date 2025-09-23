# How to sign the executable on Linux

## Self-signed certificate

:::{note}
Here is just a quick view. Read [the official documentation](https://docs.openssl.org/3.0/).
:::

### System requirements

- openssl >= 3.0
- [GitHub CLI](https://cli.github.com/)

### Step-by-step

1. Generate a private key:

    ```sh
    openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out builder/code_signing_certificate_priv.key
    ```

1. Generate a Certificate Signing Request (CSR):

    ```sh
    openssl req -new -config builder/codesign_openssl.cnf -key builder/code_signing_certificate_priv.key -out builder/code_signing_certificate_request.csr
    ```

1. Generate the self-signed certificate (CRT) with the Code Signing EKU extension:

    ```sh
    openssl x509 -req -days 3650 -in builder/code_signing_certificate_request.csr -signkey builder/code_signing_certificate_priv.key -extfile builder/codesign_openssl.cnf -extensions codesign_ext -out builder/code_signing_certificate.crt
    ```

1. Export the certificate and private key to a password-protected PFX file:

    ```sh
    openssl pkcs12 -export -out builder/code_signing_certificate.pfx -inkey builder/code_signing_certificate_priv.key -in builder/code_signing_certificate.crt
    ```

    You will be prompted to set a password. If you're part of Oslandia, search for `qdt_signing_pfx` in the internal passwords manager.

At this moment, 5 files have been generated (in order of appearance):

- `builder/codesign_openssl.cnf`: the config file
- `builder/code_signing_certificate_priv.key`: the private key - **THIS FILE SHOULD NEVER BE TRACKED WITH A PUBLIC GIT REPOSITORY**
- `builder/code_signing_certificate.crt`: the self-signed certificate
- `builder/code_signing_certificate_request.csr`: the certificate signing request
- `builder/code_signing_certificate.pfx`: the combined certificate and private key with password used to sign the Windows binary **THIS FILE SHOULD NEVER BE TRACKED WITH A PUBLIC GIT REPOSITORY**

### Check certificate

Get basic information:

```sh
openssl pkcs12 -info -in builder/code_signing_certificate.pfx -noout -subject
```

Get the thumbprint using:

```sh
openssl pkcs12 -in builder/code_signing_certificate.pfx -nodes | openssl x509 -noout -fingerprint -sha1
```

Export as PEM then in human readable text:

```sh
openssl pkcs12 -in builder/code_signing_certificate.pfx -nokeys -clcerts -out cert.pem
openssl x509 -in cert.pem -text -noout
# or just the subject
openssl x509 -in cert.pem -noout -subject
```

### Use the certificate in CI

:::{note}
This part is reserved to QDT maintainers.
:::

1. Upload the password used to export the PFX as Github Action secret:

    ```sh
    gh secret set WINDOWS_CERTIFICATE_PFX_PASSWORD
    ```

    Then paste the password.

1. Encode the PFX file as base64 for safe storage in environment variables:

    ```sh
    base64 -w0 builder/code_signing_certificate.pfx > builder/code_signing_certificate.pfx.b64
    ```

1. Upload it as Github Action secret:

    ```sh
    gh secret set WINDOWS_CERTIFICATE_PFX < builder/code_signing_certificate.pfx.b64
    ```

## Resources

- [Automatic Code-signing on Windows using GitHub Actions](https://federicoterzi.com/blog/automatic-codesigning-on-windows-using-github-actions/)
