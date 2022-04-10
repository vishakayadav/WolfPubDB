"""
Test Cases for Query Generator Module
"""
import pytest
from wolfpub.api.utils.custom_exceptions import UnauthorizedOperation

from wolfpub.api.handlers.account import AccountHandler
from wolfpub.api.handlers.distributor import DistributorHandler
from wolfpub.api.utils.mariadb_connector import MariaDBConnector

distributor_handler = DistributorHandler(MariaDBConnector())
account_handler = AccountHandler(MariaDBConnector())
distributor_data = {
    "name": "ABC",
    "distributor_type": "Whole Seller",
    "address": "string",
    "city": "raleigh",
    "phone_number": "9193137864",
    "contact_person": "Aryan"
}


class TestSetDistributor(object):
    """
    Test Cases for insert distributor
    """

    def test_set_distributor(self, mocker, mock_mysql, distributors_table, mock_table):
        """
        Positive Test Case:
        """
        mocker.patch('wolfpub.api.utils.mariadb_connector.MariaDBConnector.connect', return_value=mock_mysql)
        output = distributor_handler.set(distributor_data)
        assert output == {'distributor_id': 1}


class TestGetDistributor(object):
    """
    Test Cases for fetching distributor details
    """

    def test_get_distributor(self, mocker, mock_mysql, distributors_table, mock_table, add_record):
        """
        Positive Test Case:
        """
        mocker.patch('wolfpub.api.utils.mariadb_connector.MariaDBConnector.connect', return_value=mock_mysql)
        output = distributor_handler.get(1)
        assert output['distributor_id'] == 1

    def test_get_distributor_not_inserted(self, mocker, mock_mysql, distributors_table, mock_table):
        """
        Negative Test Case:
        """
        mocker.patch('wolfpub.api.utils.mariadb_connector.MariaDBConnector.connect', return_value=mock_mysql)
        with pytest.raises(IndexError):
            distributor_handler.get(1)


class TestUpdateDistributor(object):
    """
    Test Cases for update Distributor
    """

    def test_update_distributor(self, mocker, mock_mysql, distributors_table, mock_table, add_record):
        """
        Positive Test Case
        """
        mocker.patch('wolfpub.api.utils.mariadb_connector.MariaDBConnector.connect', return_value=mock_mysql)
        output = distributor_handler.update(1, distributor_data)
        assert output == 1

    def test_update_distributor_with_no_update(self, mocker, mock_mysql, distributors_table, mock_table, add_record):
        """
        Positive Test Case
        """
        mocker.patch('wolfpub.api.utils.mariadb_connector.MariaDBConnector.connect', return_value=mock_mysql)
        output = distributor_handler.update(2, distributor_data)
        assert output == 0


class TestDeleteDistributor(object):
    """
    Test Cases for soft delete Distributor
    """

    def test_delete_distributor_with_outstanding_balance(self, mocker, mock_mysql,
                                                distributors_table, accounts_table,
                                                mock_table, add_record):
        """
        Negative Test Case
        """
        mocker.patch('wolfpub.api.utils.mariadb_connector.MariaDBConnector.connect', return_value=mock_mysql)
        with pytest.raises(UnauthorizedOperation):
            distributor_handler.remove(1)
