from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie,csrf_exempt
from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController
# import requests

merchant_loginID=settings.MERCHANT['API_ID']
merchant_transaction_key=settings.MERCHANT['TRANSACTION_KEY']
# Create your views here.
"""
Charge a credit card
"""
def charge_credit_card(amount,card_number,card_cvc,card_name,card_expiry):
    """
    Charge a credit card
    """

    # Create a merchantAuthenticationType object with authentication details
    # retrieved from the constants file
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = merchant_loginID
    merchantAuth.transactionKey = merchant_transaction_key
    # print(merchant_loginID)

    # Create the payment data for a credit card
    creditCard = apicontractsv1.creditCardType()
    creditCard.cardNumber = '5424000000000015'
    creditCard.expirationDate = '2025-12'
    creditCard.cardCode = '999'

    # Add the payment data to a paymentType object
    payment = apicontractsv1.paymentType()
    payment.creditCard = creditCard

    # # Create order information
    # order = apicontractsv1.orderType()
    # order.invoiceNumber = "10101"
    # order.description = "Golf Shirts"

    # # Set the customer's Bill To address
    # customerAddress = apicontractsv1.customerAddressType()
    # customerAddress.firstName = "Ellen"
    # # customerAddress.lastName = "Johnson"
    # # customerAddress.company = "Souveniropolis"
    # # customerAddress.address = "14 Main Street"
    # # customerAddress.city = "Pecan Springs"
    # # customerAddress.state = "TX"
    # # customerAddress.zip = "44628"
    # # customerAddress.country = "USA"

    # # Set the customer's identifying information
    # customerData = apicontractsv1.customerDataType()
    # customerData.type = "individual"
    # customerData.id = "99999456654"
    # customerData.email = "EllenJohnson@example.com"
    

    # Add values for transaction settings
    duplicateWindowSetting = apicontractsv1.settingType()
    duplicateWindowSetting.settingName = "testRequest"
    duplicateWindowSetting.settingValue = "false"
    settings = apicontractsv1.ArrayOfSetting()
    settings.setting.append(duplicateWindowSetting)

    # setup individual line items
    line_item_1 = apicontractsv1.lineItemType()
    line_item_1.itemId = "78654"
    line_item_1.name = "first"
    line_item_1.description = "Here's the first line item"
    line_item_1.quantity = "2"
    line_item_1.unitPrice = "12.95"
    line_item_2 = apicontractsv1.lineItemType()
    line_item_2.itemId = "62290"
    line_item_2.name = "second"
    line_item_2.description = "Here's the second line item"
    line_item_2.quantity = "3"
    line_item_2.unitPrice = "7.95"

    # build the array of line items
    line_items = apicontractsv1.ArrayOfLineItem()
    line_items.lineItem.append(line_item_1)
    line_items.lineItem.append(line_item_2)

    # Create a transactionRequestType object and add the previous objects to it.
    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = "authCaptureTransaction"
    transactionrequest.amount = amount
    transactionrequest.payment = payment
    # transactionrequest.order = order
    # transactionrequest.billTo = customerAddress
    # transactionrequest.customer = customerData
    # transactionrequest.transactionSettings = settings
    transactionrequest.lineItems = line_items

    # Assemble the complete transaction request
    createtransactionrequest = apicontractsv1.createTransactionRequest()
    createtransactionrequest.merchantAuthentication = merchantAuth
    createtransactionrequest.refId = "MerchantID-0001"
    createtransactionrequest.transactionRequest = transactionrequest

    # Create the controller
    createtransactioncontroller = createTransactionController(
        createtransactionrequest)
    # https://apitest.authorize.net/xml/v1/request.api
    createtransactioncontroller.setenvironment('https://api.authorize.net/xml/v1/request.api')
    createtransactioncontroller.execute()
    response = createtransactioncontroller.getresponse()
    if response is not None:
        # Check to see if the API request was successfully received and acted upon
        if response.messages.resultCode == "Ok":
            # Since the API request was successful, look for a transaction response
            # and parse it to display the results of authorizing the card
            if hasattr(response.transactionResponse, 'messages') is True:
                print(
                    'Successfully created transaction with Transaction ID: %s'
                    % response.transactionResponse.transId)
                print('Transaction Response Code: %s' %
                      response.transactionResponse.responseCode)
                print('Message Code: %s' %
                      response.transactionResponse.messages.message[0].code)
                print('Description: %s' % response.transactionResponse.
                      messages.message[0].description)
            else:
                print('Failed Transaction. <<<<<<<<<<<<<API REQUEST SUCCESSFULL')
                if hasattr(response.transactionResponse, 'errors') is True:
                    print('Error Code:  %s' % str(response.transactionResponse.
                                                  errors.error[0].errorCode))
                    print(
                        'Error message: %s' %
                        response.transactionResponse.errors.error[0].errorText)
        # Or, print errors if the API request wasn't successful
        else:
            print('Failed Transaction.<<<<<<<<<API REQUEST NOT SUCCESSFUL')
            if hasattr(response, 'transactionResponse') is True and hasattr(
                    response.transactionResponse, 'errors') is True:
                print('Error Code: %s' % str(
                    response.transactionResponse.errors.error[0].errorCode))
                print('Error message: %s' %
                      response.transactionResponse.errors.error[0].errorText)
            else:
                print('Error Code: %s' %
                      response.messages.message[0]['code'].text)
                print('Error message: %s' %
                      response.messages.message[0]['text'].text)
    else:
        print('Null Response.')

    return response


@csrf_exempt
def create_api_call(request):
    if request.method=='POST':
        card_number=request.POST.get('number')
        card_name=request.POST.get('name')
        card_cvc=request.POST.get('cvc')
        card_expiration=request.POST.get('expiry')
        response=charge_credit_card("9.90",card_number,card_cvc,card_name,card_expiration)
        print(response)
        return render(request,'credit/thanking.html')
        
